from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess
app = Flask(__name__)

if not os.path.exists("static"):
    os.makedirs("static")

base_dir = "/var/www/sl1cer"

def get_jobs():
    jobs = []
    filenames = os.listdir(f"{base_dir}/static")
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
        stl_file.save(f"{base_dir}/static/{stl_filename}")
        supports_status = "enabled" if "supports" in request.form else "disabled"

        sl1_filename = f"{stl_filename.rsplit('.stl', 1)[0]}.sl1"
        prusa_cmd = ["prusa-slicer", "--load", f"{base_dir}/config_supports_{supports_status}.ini", "--sla", f"{base_dir}/static/{stl_filename}", "--output", f"{base_dir}/static/{sl1_filename}"]
        subprocess.run(prusa_cmd)
        if sl1_filename in os.listdir(f"{base_dir}/static"):
            pwma_filename = f"{stl_filename.rsplit('.stl', 1)[0]}.pwma"
            uvtools_cmd = ["uvtools", "--cmd", "convert", f"{base_dir}/static/{sl1_filename}", "auto", f"{base_dir}/static/{pwma_filename}"]
            subprocess.run(uvtools_cmd)

    return render_template("index.html", jobs=get_jobs())

# Remove a file from the list by removing it from the filesystem
@app.route("/remove/<stl_file>")
def remove(stl_file):
    stl_path = f"{base_dir}/static/{stl_file}"
    sl1_path = f"{base_dir}/static/{stl_file.rsplit('.stl', 1)[0]}.sl1"
    pwma_path = f"{base_dir}/static/{stl_file.rsplit('.stl', 1)[0]}.pwma"
    try:
        os.remove(stl_path)
    except:
        pass
    try:
        os.remove(sl1_path)
    except:
        pass
    try:
        os.remove(pwma_path)
    except:
        pass
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
