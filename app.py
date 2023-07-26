from flask import Flask, render_template, send_file, request
import os
import subprocess
app = Flask(__name__)

if not os.path.exists("static"):
    os.makedirs("static")

def get_jobs():
    jobs = []
    filenames = os.listdir("static")
    stl_filenames = [filename.rsplit(".stl", 1)[0] for filename in filenames if filename.endswith(".stl")]
    sl1_filenames = [filename.rsplit(".sl1", 1)[0] for filename in filenames if filename.endswith(".sl1")]
    pwma_filenames = [filename.rsplit(".pwma", 1)[0] for filename in filenames if filename.endswith(".pwma")]
    for filename in stl_filenames:
        job = {"stl_file": f"{filename}.stl", "sl1_file": "", "pwma_file": ""}
        if filename in sl1_filenames:
            job["sl1_file"] = f"{filename}.sl1"
            if filename in pwma_filenames:
                job["pwma_file"] = f"{filename}.pwma"
        jobs.append(job)
    return jobs

# Homepage - page displays a list of jobs, their status, and a link to download pwma file, and contains a basic upload form that posts to itself
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        stl_file = request.files["stl_file"]
        stl_filename = stl_file.filename.replace(" ", "_").lower()
        stl_file.save(f"static/{stl_filename}")
        supports_status = "enabled" if "supports" in request.form else "disabled"

        prusa_cmd = ["prusa-slicer", "--load", f"config_supports_{supports_status}.ini", "--sla", f"static/{stl_filename}"]
        subprocess.run(prusa_cmd)
        sl1_filename = f"{stl_filename.rsplit('.stl', 1)[0]}.sl1"
        if sl1_filename in os.listdir("static"):
            uvtools_cmd = ["uvtools", "--cmd", "convert", f"static/{sl1_filename}", "auto"]
            subprocess.run(uvtools_cmd)

    return render_template("index.html", jobs=get_jobs())

if __name__ == "__main__":
    app.run(debug=True)
