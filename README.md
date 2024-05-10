# MusicSynthesiser-BUAA
2022级42系信号与系统大作业题目四-音乐合成器
## 需求分析
- 接受一个MIDI文件，输出一个.wav音频
## 模块定义
### 音符类 Note
- 成员变量
     - pos    位置，int型，单位为采样点
     - velo   响度，float64型
     - dura   时长，int型，单位为采样点
     - pitch  音高，int型，单位为Hz
     - tone   音色，Tone类
     - env    包络，Enveloper类
    
- 成员函数wave()
    - 返回在**时域**上的序列
### MIDI解析器 MIDIParser
 - 一个生成器函数，返回一个生成器。每次迭代时，返回一个Note对象
 - 无可调超参数
### 包络类 Enveloper
 - 成员变量
	 - .A    Attack参数，int型，从乐器响起到音量达到最大的时间，单位为采样点
	 - .D    Decay参数，int型，从音量最大状态到持续状态的时间，单位为采样点
	 - .S    Sustain参数，float64型，范围为0-1，声音在持续状态中保持的音量
	 - .R    Release参数，int型，从持续时间结束到声音消失的时间，单位为采样点
### 音色类 Tone
 - 成员变量
	 - amp    float64型数组，数组第n项为第n次谐波的振幅
	 - pha     float64型数组，数组第n项为第n次谐波的相位
### 主模块 main
 - 使用以上模块，生成音频数组，并使用内置的wave模块生成.wav音频
 - 超参数用于设置BPM，整体响度等，也可以做全局的频率响应(可选)