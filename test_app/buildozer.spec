[app]

title = Test App
package.name = testapp
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
#requirements = python3,kivy
requirements = python3==3.12.4,sqlite3==3.17.15,kivy==2.3.0

orientation = portrait
fullscreen = 0
android.arch = armeabi-v7a

# iOS specific
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.7.0

[buildozer]
log_level = 2
