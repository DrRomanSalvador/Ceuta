"""Constitutional COORDINATOR and ESPEJO runtime.

Extends the existing control-plane and append-only event log; it is not a
second mission registry.
"""
from __future__ import annotations
import copy, json, os, tempfile, uuid
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterator
from .event_log import append_payload
try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

STATE_PATH=Path(__file__).with_name("COORDINATION_STATE.json")
EVENT_PATH=Path(__file__).with_name("MISSION_EVENT_LOG.jsonl")

class Authority(str,Enum):
    HUMAN="HUMAN_AUTHORITY"; CONSTITUTION="CONSTITUTION"; SECURITY="SECURITY"; COORDINATOR="COORDINATOR"; MISSION="MISSION_CONTRACT"; AGENT="AGENT_PREFERENCE"; MIRROR="MIRROR_PREFERENCE"
class CommandType(str,Enum):
    CONTINUE="CONTINUE"; CHECKPOINT="CHECKPOINT"; SPLIT="SPLIT"; REQUEST_MIRROR="REQUEST_MIRROR"; PAUSE="PAUSE"; STANDBY="STANDBY"; RESUME="RESUME"; REDIRECT="REDIRECT"; DELEGATE="DELEGATE"; HANDOFF="HANDOFF"; RECOVER="RECOVER"; ABANDON="ABANDON"; REPRIORITIZE="REPRIORITIZE"
class CommandState(str,Enum):
    ISSUED="ISSUED"; ACKNOWLEDGED="ACKNOWLEDGED"; EXECUTING="EXECUTING"; COMPLETED="COMPLETED"; REJECTED="REJECTED"; CONFLICT="COMMAND_CONFLICT"
class MirrorAction(str,Enum):
    ASSIST="ASSIST"; REVIEW="REVIEW"; VERIFY="VERIFY"; RESEARCH="RESEARCH"; TEST="TEST"; RED_TEAM="RED_TEAM"; CHECKPOINT="CHECKPOINT"; RECOVERY="RECOVERY"; PREPARE="PREPARE"
class MirrorState(str,Enum):
    REQUESTED="REQUESTED"; OBSERVING="OBSERVING"; AUTHORITY_CHECKED="AUTHORITY_CHECKED"; ASSIGNED="ASSIGNED"; EXECUTING="EXECUTING"; VALIDATING="VALIDATING"; PERSISTED="PERSISTED"; HANDOFF="HANDOFF"; RETURNED="RETURNED"; CONFLICT="CONFLICT"
class CoordinationError(ValueError): pass
class StaleStateError(CoordinationError): pass
class CommandConflict(CoordinationError): pass
class OwnershipConflict(CoordinationError): pass

def utc_now(): return datetime.now(timezone.utc).isoformat()
def _initial_state():
    return {"schema_version":"1.1.0","state_version":0,"updated_at":utc_now(),"agents":{},"missions":{},"tasks":{},"priorities":{},"checkpoints":{},"commands":{},"interventions":[],"mirrors":{},"standby":{},"recovery":[],"conflicts":[],"handoffs":[],"pending_reviews":[],"deferred_hypotheses":{}}
@contextmanager
def _locked(path:Path)->Iterator[None]:
    lock=path.with_suffix(path.suffix+".lock"); lock.parent.mkdir(parents=True,exist_ok=True)
    with lock.open("a+",encoding="utf-8") as h:
        if fcntl is not None: fcntl.flock(h.fileno(),fcntl.LOCK_EX)
        try: yield
        finally:
            if fcntl is not None: fcntl.flock(h.fileno(),fcntl.LOCK_UN)
@dataclass(frozen=True)
class Command:
    order_id:str; issuer:str; target:str; mission:str; reason:str; authority_basis:str; issued_at:str; state:str; expected_effect:str; acknowledgement:str|None; execution_result:str|None; command_type:str; expected_version:int; reversible:bool; provenance:dict[str,str]
@dataclass(frozen=True)
class MirrorInvocation:
    mirror_id:str; mirror_of:str; mission:str; target_agent:str; task:str; problem:str; capability_required:str; limits:tuple[str,...]; priority:str; authority:str; expected_result:str; action:str; functional_role:str; state:str; mission_owner:str; subtask_owner:str; provenance:dict[str,str]
@dataclass(frozen=True)
class DeferredHypothesis:
    hypothesis_id:str; author:str; timestamp:str; context:str; reasoning:str; alternative_proposed:str; suspension_reason:str

class CoordinationStore:
    def __init__(self,state_path:Path=STATE_PATH,event_path:Path=EVENT_PATH): self.state_path=Path(state_path); self.event_path=Path(event_path)
    def load(self):
        if not self.state_path.exists(): return _initial_state()
        data=json.loads(self.state_path.read_text(encoding="utf-8")); self._validate(data); return data
    @staticmethod
    def _validate(data):
        missing=set(_initial_state())-set(data)
        if missing: raise CoordinationError(f"coordination state missing fields: {sorted(missing)}")
        if not isinstance(data.get("state_version"),int) or data["state_version"]<0: raise CoordinationError("invalid coordination state_version")
        if data.get("schema_version") not in {"1.0.0","1.1.0"}: raise CoordinationError("unsupported coordination schema")
    def _write(self,data):
        self._validate(data); self.state_path.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(prefix="coordination-",suffix=".json",dir=self.state_path.parent)
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as h: json.dump(data,h,sort_keys=True,indent=2,ensure_ascii=False); h.flush(); os.fsync(h.fileno())
            os.replace(tmp,self.state_path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    def mutate(self,*,actor,event_type,mission_id,expected_version,mutation):
        with _locked(self.state_path):
            state=self.load(); current=state["state_version"]
            if expected_version is not None and expected_version!=current: raise StaleStateError(f"expected coordination version {expected_version}, observed {current}")
            new=copy.deepcopy(state); mutation(new); new["schema_version"]="1.1.0"; new["state_version"]=current+1; new["updated_at"]=utc_now(); self._write(new)
            append_payload(self.event_path,event_type=event_type,mission_id=mission_id,actor=actor,timestamp=new["updated_at"],payload={"state_version":new["state_version"],"state":event_type})
            return new

class Coordinator:
    IDENTITY="COORDINATOR"; COMMANDS=frozenset(CommandType)
    def __init__(self,*,instance_id=None,store=None): self.instance_id=instance_id or f"COORD-{uuid.uuid4().hex[:12]}"; self.store=store or CoordinationStore()
    def observe(self):
        s=self.store.load(); return {"instance_id":self.instance_id,**{k:copy.deepcopy(s[k]) for k in ("agents","missions","tasks","priorities","checkpoints","commands","mirrors","standby","conflicts","recovery","handoffs","pending_reviews")},"state_version":s["state_version"]}
    def register_agent(self,agent_id,mission_id,*,state="ACTIVE",progress=True,expected_version=None):
        def m(s): s["agents"][agent_id]={"agent_id":agent_id,"mission_id":mission_id,"state":state,"progress":bool(progress),"last_heartbeat":utc_now(),"last_checkpoint":None,"last_change":utc_now()}
        return self.store.mutate(actor=self.instance_id,event_type="COORDINATOR_AGENT_REGISTERED",mission_id=mission_id,expected_version=expected_version,mutation=m)
    def update_observation(self,agent_id,*,state,progress,last_checkpoint=None,expected_version=None):
        mission=self.store.load()["agents"].get(agent_id,{}).get("mission_id","UNKNOWN")
        def m(s):
            if agent_id not in s["agents"]: raise CoordinationError("unknown agent")
            s["agents"][agent_id].update({"state":state,"progress":bool(progress),"last_heartbeat":utc_now(),"last_change":utc_now()})
            if last_checkpoint is not None: s["agents"][agent_id]["last_checkpoint"]=last_checkpoint
        return self.store.mutate(actor=self.instance_id,event_type="COORDINATOR_OBSERVATION",mission_id=mission,expected_version=expected_version,mutation=m)
    def issue(self,*,command_type,target,mission,reason,authority_basis,expected_effect,expected_version=None,reversible=True,order_id=None):
        if command_type not in self.COMMANDS: raise CoordinationError("unsupported coordinator command")
        if authority_basis not in {Authority.COORDINATOR.value,Authority.HUMAN.value}: raise CommandConflict("coordinator command lacks valid operational authority basis")
        if command_type in {CommandType.REDIRECT,CommandType.ABANDON} and authority_basis!=Authority.HUMAN.value: raise CommandConflict(f"{command_type.value} requires superior/human authority")
        current=self.store.load(); v=current["state_version"]
        if expected_version is not None and expected_version!=v: raise StaleStateError(f"expected coordination version {expected_version}, observed {v}")
        oid=order_id or f"ORD-{uuid.uuid4().hex}"; existing=current["commands"].get(oid)
        if existing:
            if all(existing.get(k)==x for k,x in (("target",target),("mission",mission),("command_type",command_type.value),("expected_effect",expected_effect))): return current
            raise CommandConflict(f"command replay/collision for order_id={oid}")
        now=utc_now(); prov={"DISCOVERED_BY":self.instance_id,"PROPOSED_BY":self.instance_id,"IMPLEMENTED_BY":self.instance_id,"REVIEWED_BY":"PENDING","VALIDATED_BY":"PENDING","AUTHORIZED_BY":authority_basis,"COMMAND_ISSUER":self.instance_id}
        c=Command(oid,self.instance_id,target,mission,reason,authority_basis,now,CommandState.ISSUED.value,expected_effect,None,None,command_type.value,v,reversible,prov)
        def m(s): s["commands"][oid]=asdict(c); s["interventions"].append({"order_id":oid,"issuer":self.instance_id,"type":command_type.value,"target":target,"mission":mission,"timestamp":now,"provenance":prov})
        return self.store.mutate(actor=self.instance_id,event_type="COORDINATOR_COMMAND_ISSUED",mission_id=mission,expected_version=v,mutation=m)
    def acknowledge(self,order_id,*,acknowledgement,expected_version=None):
        mission=self.store.load()["commands"].get(order_id,{}).get("mission","UNKNOWN")
        def m(s):
            c=s["commands"].get(order_id)
            if not c: raise CoordinationError("unknown command")
            if c["state"] not in {CommandState.ISSUED.value,CommandState.ACKNOWLEDGED.value}: raise CoordinationError("command cannot be acknowledged")
            c["state"]=CommandState.ACKNOWLEDGED.value; c["acknowledgement"]=acknowledgement
        return self.store.mutate(actor=self.instance_id,event_type="COORDINATOR_COMMAND_ACKNOWLEDGED",mission_id=mission,expected_version=expected_version,mutation=m)
    def record_execution(self,order_id,*,result,success,expected_version=None):
        mission=self.store.load()["commands"].get(order_id,{}).get("mission","UNKNOWN")
        def m(s):
            c=s["commands"].get(order_id)
            if not c: raise CoordinationError("unknown command")
            c["state"]=CommandState.COMPLETED.value if success else CommandState.REJECTED.value; c["execution_result"]=result; c["provenance"]["VALIDATED_BY"]=self.instance_id
        return self.store.mutate(actor=self.instance_id,event_type="COORDINATOR_COMMAND_RESULT",mission_id=mission,expected_version=expected_version,mutation=m)
    def request_mirror(self,*,target_agent,mission,task,problem,capability_required,limits,priority,authority,expected_result,expected_version=None,order_id=None):
        return self.issue(command_type=CommandType.REQUEST_MIRROR,target=target_agent,mission=mission,reason=f"task={task}; capability={capability_required}; limits={limits}; priority={priority}; problem={problem}",authority_basis=authority,expected_effect=expected_result,expected_version=expected_version,order_id=order_id)
    def checkpoint_then_pause(self,*,target,mission,checkpoint_id,expected_version=None):
        def m(s): s["checkpoints"][checkpoint_id]={"checkpoint_id":checkpoint_id,"mission":mission,"target":target,"created_at":utc_now(),"state":"PERSISTED"}
        s=self.store.mutate(actor=self.instance_id,event_type="COORDINATOR_CHECKPOINT",mission_id=mission,expected_version=expected_version,mutation=m)
        return self.issue(command_type=CommandType.PAUSE,target=target,mission=mission,reason="safe pause after checkpoint",authority_basis=Authority.COORDINATOR.value,expected_effect="paused with recoverable checkpoint",expected_version=s["state_version"])
    def standby(self,*,target,mission,checkpoint_id,expected_version=None):
        if checkpoint_id not in self.store.load()["checkpoints"]: raise CoordinationError("STANDBY requires a persisted checkpoint")
        return self.issue(command_type=CommandType.STANDBY,target=target,mission=mission,reason="temporary operational standby",authority_basis=Authority.COORDINATOR.value,expected_effect="identity and recoverability preserved",expected_version=expected_version)
    def detect_execution(self,agent_id):
        a=self.store.load()["agents"].get(agent_id)
        if not a: raise CoordinationError("unknown agent")
        if a["state"]=="ACTIVE" and a["progress"]: return "ACTIVE_PROGRESSING_NO_INTERVENTION"
        if a["state"]=="ACTIVE": return "ACTIVE_NO_PROGRESS_REVIEW"
        if a["state"] in {"RUNNING","EXECUTING"} and a["progress"]: return "LONG_RUNNING_PROGRESS_CONTINUE"
        if a["state"] in {"RUNNING","EXECUTING"}: return "LONG_RUNNING_NO_PROGRESS_REVIEW"
        return "OBSERVE_AND_CLASSIFY"
    def persist_deferred_hypothesis(self,hypothesis,*,mission_id,expected_version=None):
        def m(s): s["deferred_hypotheses"][hypothesis.hypothesis_id]=asdict(hypothesis)
        return self.store.mutate(actor=self.instance_id,event_type="DEFERRED_HYPOTHESIS",mission_id=mission_id,expected_version=expected_version,mutation=m)

class Mirror:
    IDENTITY="ESPEJO"; ACTIONS=frozenset(MirrorAction)
    def __init__(self,*,instance_id=None,store=None): self.instance_id=instance_id or f"MIRROR-{uuid.uuid4().hex[:12]}"; self.store=store or CoordinationStore()
    def invoke(self,*,mirror_of,mission,target_agent,task,problem,capability_required,limits,priority,authority,expected_result,action,functional_role,mission_owner):
        if action not in self.ACTIONS: raise CoordinationError("unsupported mirror action")
        if authority not in {Authority.COORDINATOR.value,Authority.HUMAN.value}: raise CommandConflict("mirror invocation requires coordinator or human authority")
        mid=f"MIR-{uuid.uuid4().hex}"; prov={"DISCOVERED_BY":self.instance_id,"PROPOSED_BY":mirror_of,"IMPLEMENTED_BY":self.instance_id,"REVIEWED_BY":"PENDING","VALIDATED_BY":"PENDING","AUTHORIZED_BY":authority,"MIRROR_OF":mirror_of}
        inv=MirrorInvocation(mid,mirror_of,mission,target_agent,task,problem,capability_required,tuple(limits),priority,authority,expected_result,action.value,functional_role,MirrorState.REQUESTED.value,mission_owner,self.instance_id,prov)
        def m(s): s["mirrors"][mid]=asdict(inv)
        return self.store.mutate(actor=self.instance_id,event_type="MIRROR_INVOCATION",mission_id=mission,expected_version=None,mutation=m)
    def claim_subtask(self,mirror_id,*,task_id,expected_version=None):
        mission=self.store.load()["mirrors"].get(mirror_id,{}).get("mission","UNKNOWN")
        def m(s):
            inv=s["mirrors"].get(mirror_id)
            if not inv: raise CoordinationError("unknown mirror invocation")
            if inv["subtask_owner"]!=self.instance_id: raise OwnershipConflict("mirror identity does not own invocation")
            t=s["tasks"].get(task_id)
            if t and t.get("subtask_owner") not in {None,self.instance_id}: raise OwnershipConflict("subtask already claimed")
            if not t: t=s["tasks"].setdefault(task_id,{"task_id":task_id,"mission":inv["mission"],"mission_owner":inv["mission_owner"],"status":"READY"})
            t.update({"subtask_owner":self.instance_id,"mirror_id":mirror_id,"status":"CLAIMED"}); inv["state"]=MirrorState.ASSIGNED.value
        return self.store.mutate(actor=self.instance_id,event_type="MIRROR_SUBTASK_CLAIMED",mission_id=mission,expected_version=expected_version,mutation=m)
    def complete(self,mirror_id,*,result,validated,expected_version=None):
        mission=self.store.load()["mirrors"].get(mirror_id,{}).get("mission","UNKNOWN")
        def m(s):
            inv=s["mirrors"].get(mirror_id)
            if not inv or inv["subtask_owner"]!=self.instance_id: raise OwnershipConflict("mirror cannot complete foreign invocation")
            if not validated: raise CoordinationError("mirror handoff requires validation")
            inv.update({"state":MirrorState.RETURNED.value,"result":result,"validated":True}); inv["provenance"]["VALIDATED_BY"]=self.instance_id
            s["handoffs"].append({"mirror_id":mirror_id,"mission_owner":inv["mission_owner"],"subtask_owner":self.instance_id,"result":result,"timestamp":utc_now(),"control_returned":True,"provenance":inv["provenance"]})
        return self.store.mutate(actor=self.instance_id,event_type="MIRROR_HANDOFF",mission_id=mission,expected_version=expected_version,mutation=m)
    def observe_recovery(self,mirror_id):
        inv=self.store.load()["mirrors"].get(mirror_id)
        if not inv: raise CoordinationError("unknown mirror invocation")
        return copy.deepcopy(inv)

__all__=["Authority","CommandType","CommandState","MirrorAction","MirrorState","Command","MirrorInvocation","DeferredHypothesis","CoordinationStore","Coordinator","Mirror","CoordinationError","StaleStateError","CommandConflict","OwnershipConflict"]
