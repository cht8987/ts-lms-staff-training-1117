import subprocess
import urllib.request

def get_session_cookie(user_id=1):
    php_code = f"""
require __DIR__ . '/vendor/autoload.php';
$app = require_once __DIR__ . '/bootstrap/app.php';
$kernel = $app->make(Illuminate\\Contracts\\Console\\Kernel::class);
$kernel->bootstrap();

$sid = Illuminate\\Support\\Str::random(40);
$s = app('session')->driver();
$s->setId($sid);
$s->start();
$s->put(Auth::guard('web')->getName(), {user_id});
$s->save();
echo app('encrypter')->encrypt($sid, false);
"""
    cmd = ["ssh", "ts-vps", f"docker exec -u www-data -e HOME=/tmp -e XDG_CONFIG_HOME=/tmp rocket_lms_php php -r \"{php_code}\""]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return p.stdout.strip()

if __name__ == "__main__":
    cookie = get_session_cookie(1)
    print("Cookie len:", len(cookie))
    
    req = urllib.request.Request("https://lms.topscholar.edu.my/admin/ts-crm/enrollments")
    req.add_header("Cookie", f"rocket_lms_session={cookie}")
    req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    with urllib.request.urlopen(req) as resp:
        print("Status:", resp.status)
        print("Final URL:", resp.url)
        content = resp.read().decode("utf-8")
        print("Length:", len(content))
        start = content.find("<title>")
        end = content.find("</title>")
        if start != -1 and end != -1:
            print("Page Title:", content[start+7:end].strip())
