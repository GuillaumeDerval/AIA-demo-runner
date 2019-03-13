from demos import json_run
from demos.custom_example import custom_demo_example

demo_handlers = [
    # see demos/custom_example.py
    custom_demo_example,
    # runs the command "echo". Expects a JSON as input.
    json_run("cat", ["/run-demo"], name="Echo", description="Send me some JSON in the post request, and I will echo it back to you."),
    # runs the script timeout_test, which should answer only after 5 secs.
    json_run("python demos/timeout_test.py", ["/run-demo-timeout-ko"], name="Timeout ko", description="Timeout demo", timeout=1.0),
    json_run("python demos/timeout_test.py", ["/run-demo-timeout-ok"], name="Timeout ok", description="Timeout demo", timeout=10.0),
    # Example of demo in java. The main should expect a json on stdin, and output a json on stdout.
    #json_run("java -jar myjar.jar arg1 arg2", ["/java-demo"], name="Mu jar demo", description="Some description.")
]
