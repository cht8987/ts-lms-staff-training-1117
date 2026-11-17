import base64
import subprocess
import urllib.request
import urllib.parse

def get_cookie(uid: int) -> str:
    php = f'''
require "vendor/autoload.php";
$app = require "bootstrap/app.php";
$kernel = $app->make(Illuminate\\Contracts\\Console\\Kernel::class);
$kernel->bootstrap();
$sid = Illuminate\\Support\\Str::random(40);
$s = app("session")->driver();
$s->setId($sid);
$s->start();
$s->put(Auth::guard("web")->getName(), {uid});
$s->save();
$prefix = Illuminate\\Cookie\\CookieValuePrefix::create(config("session.cookie"), app("encrypter")->getKey());
$cookie = app("encrypter")->encrypt($prefix . $sid, false);
echo "COOKIE:" . $cookie . "\\n";
'''
    b64 = base64.b64encode(php.encode()).decode()
    cmd = ["ssh", "ts-vps", f'docker exec -u www-data -e HOME=/tmp -w /var/www/html rocket_lms_php php -r "eval(base64_decode(\'{b64}\'));"']
    out = subprocess.check_output(cmd).decode()
    for line in out.splitlines():
        if line.startswith("COOKIE:"):
            return line[7:].strip()
    raise RuntimeError("No cookie returned: " + out)

if __name__ == "__main__":
    adm_c = get_cookie(1)
    stu_c = get_cookie(50956)

    def check(url, cookie):
        req = urllib.request.Request("https://lms.topscholar.edu.my" + url)
        req.add_header("Cookie", f"rocket_lms_session={urllib.parse.quote(cookie)}")
        req.add_header("User-Agent", "Mozilla/5.0")
        try:
            with urllib.request.urlopen(req) as r:
                body = r.read().decode("utf-8", errors="ignore")
                t = body[body.find("<title>"):body.find("</title>")+8] if "<title>" in body else ""
                print(f"OK {r.status} {url} -> {r.url} | {t.strip()}")
        except Exception as e:
            print(f"ERR {url} -> {e}")

    for u in [
        "/admin/ts-crm/enrollments",
        "/admin/ts-crm/enrollment/create",
        "/admin/ts-crm/enrollment/5375953/edit",
        "/admin/ts-crm/enrollment/5375953/payments",
        "/admin/ts-crm/enrollment/5375953/invoice",
        "/admin/ts-crm/enrollment/5375953/receipt",
        "/admin/ts-crm/students/11960",
        "/admin/ts-crm/students/45253",
        "/admin/ts-crm/students/16493",
        "/admin/ts-crm/students/50956",
        "/admin/ts-crm/students/11960/edit",
        "/admin/ts-crm/students/45253/edit",
        "/admin/ts-crm/students/11960/change-time",
        "/admin/ts-crm/students/11960/swap-class",
        "/admin/ts-crm/students/11960/transfer",
        "/admin/ts-homework",
        "/admin/ts-homework/2352/edit",
        "/admin/ts-homework/190/submissions",
        "/admin/ts-homework/190/submissions/50956",
        "/admin/ts-care/class-records",
        "/admin/ts-care/student/11960",
        "/admin/ts-care/student/16493",
    ]:
        check(u, adm_c)

    for u in [
        "/panel",
        "/panel/ts-homework",
        "/panel/ts-homework/2352",
        "/panel/ts-homework/190",
        "/panel/setting",
        "/panel/bana/go",
        "/login",
    ]:
        check(u, stu_c)
