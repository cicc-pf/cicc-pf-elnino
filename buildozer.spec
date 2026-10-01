[app]

title = CICC PF El Nino
package.name = ciccpfelnino
package.domain = br.gov.am.presidentefigueiredo.cicc

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 0.1.0

requirements = python3,kivy==2.3.1,kivymd==1.2.0,pyjnius==1.7.0,requests,urllib3,certifi,charset-normalizer,idna,pillow

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, ACCESS_NETWORK_STATE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

android.debug_artifact = True
android.wakelock = False

p4a.branch = v2023.09.16

[buildozer]

log_level = 2
warn_on_root = 1
