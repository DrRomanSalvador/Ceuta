import multiprocessing as mp
import tempfile
import unittest
from pathlib import Path

from .materialized_state import compare_and_swap_mission, read_mission


def _cas_worker(path: str, mission_id: str, expected_revision: int, projection: dict, queue):
    try:
        result=compare_and_swap_mission(Path(path),mission_id,expected_revision,projection)
        queue.put(("ACQUIRED",result))
    except Exception as exc:
        queue.put(("REJECTED",str(exc)))

class MaterializedStateTests(unittest.TestCase):
    def test_same_mission_has_one_winner_and_one_stale_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"state.json"; queue=mp.get_context("spawn").Queue()
            workers=[mp.get_context("spawn").Process(target=_cas_worker,args=(str(path),"ROMAN",0,{"status":f"writer-{i}"},queue)) for i in range(2)]
            for p in workers: p.start()
            for p in workers: p.join()
            results=[queue.get() for _ in workers]
            self.assertTrue(all(p.exitcode==0 for p in workers))
            self.assertEqual([r[0] for r in results].count("ACQUIRED"),1)
            self.assertEqual([r[0] for r in results].count("REJECTED"),1)
            self.assertEqual(read_mission(path,"ROMAN")["revision"],1)

    def test_independent_missions_do_not_conflict(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"state.json"
            compare_and_swap_mission(path,"ROMAN",0,{"status":"A"})
            compare_and_swap_mission(path,"ESPIONA",0,{"status":"B"})
            self.assertEqual(read_mission(path,"ROMAN")["revision"],1)
            self.assertEqual(read_mission(path,"ESPIONA")["revision"],1)

    def test_stale_writer_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"state.json"
            compare_and_swap_mission(path,"ROMAN",0,{"status":"A"})
            with self.assertRaises(ValueError): compare_and_swap_mission(path,"ROMAN",0,{"status":"STALE"})
            self.assertEqual(read_mission(path,"ROMAN")["projection"]["status"],"A")

if __name__=="__main__": unittest.main()
