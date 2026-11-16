---
title: AesirTimer
description: "Runestone.AesirArchitecture.AesirTimer 的 API 文档"
---

# `AesirTimer`

!!! note ""

    - **种类:** `class`
    - **命名空间:** `Runestone.AesirArchitecture`
    - **程序集:** `Runestone.AesirArchitecture`

**继承链:** `System.Object` → `AesirTimer`

**实现接口:** `System.IDisposable`

## 声明

``` csharp
public sealed class AesirTimer : System.IDisposable
```

框架驱动的计时器：创建即开始、到期自动出队，可随时查询剩余时间与进度。
定位是"拿不到每帧回调的地方"的计时手段——纯 C# 的 Model / Service / Command 不需要 MonoBehaviour、也不需要协程即可延时、冷却、按间隔重复。 能拿到每帧回调的地方（MonoBehaviour.Update 或 MonoLifecycleProxy） 应直接用一个 float 字段累减，不必创建计时器。

每个计时器是一个独立实例：时长、剩余时间、时间源、到期回调都挂在实例字段上， 注册表只保存"哪些实例还活着"用于每帧推进。因此调用方可以持有引用来查询 Progress（供 UI 进度条使用），也可以在创建后直接丢弃引用（框架代持至到期）。

**备注**

为什么是引用类型而不是值类型：框架需要"替你推进"并且"你随时能查"。 可变结构体在这里会失效——注册表持有的是副本，推进的是副本，调用方读到的仍是旧值； 引用类型让注册表与调用方操作同一个实例。

为什么没有 Start / Pause / Resume / Tick：工厂方法即开始， 不存在"创建了但没跑"的中间态；游戏暂停由 Time.timeScale 表达（默认时间源跟随缩放）， "暂停单个计时器"是低频需求，用 Cancel 加重建即可； 不自带 Tick 是为了不与已有的 Update 路径重复。

注入方式：经 AesirPlayerLoop 的 BeforeUpdate 钩子推进，order 取 MinValue——计时结算先于任何用户钩子， 语义是本帧先结算计时再跑业务逻辑；该 order 也是用户无法抢占的稳定锚点。 复用 AesirPlayerLoop 而非自行调用 PlayerLoop.SetPlayerLoop， 可直接获得 EnsureInjected 的自愈能力（第三方 SDK 覆盖 PlayerLoop 后不会让计时器静默失效）。

症状与代价：帧粒度结算，误差在 ±1 帧内，不做亚帧精度保证，也不做绝对时间校准。 每个计时器一次堆分配（生命周期短，落在 Gen0）；框架不做对象池，需要复用同一冷却位时用 Restart。

## 属性

<div class="api-summary-table" markdown="1">

| 名称 | 描述 |
| :--- | :--- |
| [`IsCancelled`](#property-iscancelled) | 是否被 Cancel 或 Dispose 取消且尚未到期。 |
| [`IsFinished`](#property-isfinished) | 是否已正常到期。被取消的计时器恒为 false（与 IsCancelled 互斥）。 |
| [`Duration`](#property-duration) | 构造时给定的时长（秒）。NextFrame 形态恒为 0。 |
| [`Progress`](#property-progress) | 已走完的比例，0 → 1，可直接用于进度条。 |
| [`Remaining`](#property-remaining) | 剩余秒数。到期或被取消后保持当时的值（到期为 0）。NextFrame 形态恒为 0。 |

</div>

### IsCancelled {#property-iscancelled}

是否被 Cancel 或 Dispose 取消且尚未到期。

**备注**

已到期的计时器调用 Cancel 不会改变任何状态：同一次结算中"到期"先于"取消"发生， 已判定到期的回调仍会执行。

``` csharp
public bool IsCancelled { get; }
```

### IsFinished {#property-isfinished}

是否已正常到期。被取消的计时器恒为 false（与 IsCancelled 互斥）。

``` csharp
public bool IsFinished { get; }
```

### Duration {#property-duration}

构造时给定的时长（秒）。NextFrame 形态恒为 0。

``` csharp
public float Duration { get; }
```

### Progress {#property-progress}

已走完的比例，0 → 1，可直接用于进度条。

**备注**

正常到期返回 1；Duration 为 0 的实例在到期前返回 0（避免 0/0 产生 NaN）； 被取消后冻结在取消时刻的值。

``` csharp
public float Progress { get; }
```

### Remaining {#property-remaining}

剩余秒数。到期或被取消后保持当时的值（到期为 0）。NextFrame 形态恒为 0。

``` csharp
public float Remaining { get; }
```

## 方法

**声明的方法**

<div class="api-summary-table" markdown="1">

| 名称 | 描述 |
| :--- | :--- |
| [`Cancel()`](#method-cancel) | 取消计时：移出结算列表、不再触发回调，状态转为 IsCancelled。 |
| [`Dispose()`](#method-dispose) | 等同于 Cancel，供 using 与句柄风格调用。 |
| [`Restart()`](#method-restart) | 重新开始计时并重新入队：剩余时间复位为 Duration， IsFinished 与 IsCancelled 一并复位。 |
| [`Countdown(float, Action, bool)`](#method-countdown-float-action-bool) | 创建一个倒计时并在同一次调用内开始计时。 |
| [`NextFrame(Action)`](#method-nextframe-action) | 创建一个"下一帧执行一次"的计时器。 |

</div>

**继承的方法**

<div class="api-summary-table" markdown="1">

| 名称 | 描述 | 声明类型 |
| :--- | :--- | :--- |
| `GetType()` | — | `object` |
| `Equals(object)` | — | `object` |
| `GetHashCode()` | — | `object` |
| `ToString()` | — | `object` |
| `MemberwiseClone()` | — | `object` |
| `Finalize()` | — | `object` |

</div>

### Cancel() {#method-cancel}

取消计时：移出结算列表、不再触发回调，状态转为 IsCancelled。

**备注**

重复调用安全。已到期的计时器调用本方法无效果（见 IsCancelled）。 取消后仍可用 Restart 重新拉起。

``` csharp
public void Cancel()
```

### Dispose() {#method-dispose}

等同于 Cancel，供 using 与句柄风格调用。

**备注**

正常到期的计时器无需释放（到期已自动出队），因此 Dispose 只对"未到期就放弃"的场景有意义。

``` csharp
public void Dispose()
```

### Restart() {#method-restart}

重新开始计时并重新入队：剩余时间复位为 Duration， IsFinished 与 IsCancelled 一并复位。

**备注**

用于"同一个冷却位反复使用"——UI 或 Model 已经持有该实例，不必换新引用。 需要不同时长时直接新建实例（框架不做对象池）。

NextFrame 形态调用本方法等价于重新挂起一次"下一帧执行"。 重复调用安全：已入队时不会重复注册。

``` csharp
public void Restart()
```

### Countdown(float, Action, bool) {#method-countdown-float-action-bool}

创建一个倒计时并在同一次调用内开始计时。

**备注**

调用即产生副作用：立即注册到框架结算列表并确保 PlayerLoop 注入完成。 返回的实例即使被丢弃也不会泄漏——到期后自动出队，只是失去 Cancel 的能力。

``` csharp
public static AesirTimer Countdown(float seconds, Action onFinished = null, bool unscaled = false)
```

**参数**

<div class="api-params-table" markdown="1">

| 名称 | 类型 | 说明 |
| :--- | :--- | :--- |
| `seconds` | `float` | 倒计时时长（秒）。零或负值立即处于到期状态，在下一次结算中回调。 |
| `onFinished` | `Action` | 到期回调，可为 null。 |
| `unscaled` | `bool` | true 时使用 Time.unscaledDeltaTime（Time.timeScale = 0 仍继续计时）， 用于暂停菜单、UI 动画等不受游戏速度影响的场景。 |

</div>

**返回值**

<div class="api-returns-table" markdown="1">

| 类型 | 说明 |
| :--- | :--- |
| `AesirTimer` | 计时器实例，持有引用可查询进度或在到期前取消 |

</div>

### NextFrame(Action) {#method-nextframe-action}

创建一个"下一帧执行一次"的计时器。

**备注**

语义是"此后第一次结算"，而不是"当前帧剩下的时间里某一次结算"：创建发生在一次结算之后 （例如 MonoBehaviour.Update、协程、或另一个计时器的到期回调中）时，回调落在下一帧； 创建发生在当帧结算之前（例如 AfterAssembliesLoaded）时，回调落在当帧的结算里。

"下一帧"是按结算周期计数的，与 Time.timeScale 无关，因此不接受 unscaled 参数。

``` csharp
public static AesirTimer NextFrame(Action onFinished)
```

**参数**

<div class="api-params-table" markdown="1">

| 名称 | 类型 | 说明 |
| :--- | :--- | :--- |
| `onFinished` | `Action` | 下一帧结算时执行的回调 |

</div>

**返回值**

<div class="api-returns-table" markdown="1">

| 类型 | 说明 |
| :--- | :--- |
| `AesirTimer` | 计时器实例（Duration 恒为 0，与倒计时共用同一套查询与取消接口） |

</div>

## Additional Notes

> 首个 `## Additional Notes` 是增量生成文档标识符，请勿修改标题级别和内容！本文档由 [`Script Doc Generator`](https://github.com/yuumixcode/AesirFramework) 辅助生成。
