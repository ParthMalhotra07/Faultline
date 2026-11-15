from faultline.evaluation.report import evaluate
import os
import tempfile

# Keep ephemeral application manifests out of Desktop indexing/synchronization.
# Database storage and preserved evaluation artifacts remain in the workspace.
with tempfile.TemporaryDirectory(prefix='faultline-eval-') as workspace:
    previous=os.getcwd()
    try:
        os.chdir(workspace)
        evaluate()
    finally:
        os.chdir(previous)
