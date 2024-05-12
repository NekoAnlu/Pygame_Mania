# PyMania

基于pygame-ce开发，判定基于OsuMania，可以读取Malody4k-9k谱面进行游玩的Malody Key模式模拟器

## 使用方法

1. clone该项目到任意文件夹，注意根目录最好不要有中文文件夹

   ```git
   git clone https://github.com/NekoAnlu/Pygame_Mania.git
   ```

2. 安装插件所需模块：`pip install -r requirements.txt`
3. 自行在Malody或点击下载链接下载谱面文件到`beatmaps`文件夹中
4. 使用powershell在项目根目录文件夹中输入`py run.py`，启动游戏

### 可能TODO：

1. 变速谱支持

### 已知BUG:

1. LN绘制导致''卡键''，即按键提示处一直为按下状态