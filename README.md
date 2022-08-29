# BiliBiliLiveUp
哔哩哔哩直播录制,基于B站录播姬和biliup-rs的全自动录播、投稿工具,只需直播间地址即可自动录制上传,自动从直播间获取封面，支持rclone上传至onedrive


首先根据微软文档安装dotnet https://docs.microsoft.com/zh-cn/dotnet/core/tools/dotnet-install-script sudo bash./dotnet-install.sh -c Current --runtime dotnet 下载cil版B站录播姬，https://github.com/BililiveRecorder/BililiveRecorder 下载并准备好cookie，https://github.com/ForgQi/biliup-rs 在hook.py旁边建一个rclone文件夹，里面放rclone的东西并配置好https://rclone.org/onedrive/ 修改hook.py的exec_path，并把'one:bil/'改成自己网盘的文件夹 运行hook.py dotnet cil/BililiveRecorder.Cli.dll run --bind "http://*:11419" "/root/b/work" 然后http://localhost:11419添加直播间，配置基本不用改
