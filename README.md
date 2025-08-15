# Agent Manager System

智能体管理系统，用于协调不同类型智能体之间的调用和通信。

## 系统架构

```
用户
  │
  ↓ (HTTP POST /api/v1/scheduler/process_query)
调度智能体（FastAPI） → 解析意图 → 调用qwen2.5模型
  │
  ↓ (返回target_agents列表)
前端 → 根据列表并发请求工作智能体
  │
  ↓ (HTTP POST /api/v1/worker/execute/{agent_id})
工作智能体1 → 处理任务 → 返回结果
工作智能体2 → 处理任务 → 返回结果
  │
前端 ← 聚合结果展示
```

## 系统特性

1. **智能体消息传递**：实现智能体之间的消息传递
2. **多类型智能体支持**：支持不同类型智能体的接入
3. **统一接口**：提供统一的接口供外部调用
4. **动态管理**：支持智能体的动态添加和删除
5. **生命周期管理**：智能体注册/心跳/状态跟踪
6. **通信规范**：统一消息格式与路由协议
7. **并发执行**：所有请求并发执行
8. **模块化设计**：支持独立智能体模块开发

## 默认智能体

系统启动时会自动注册以下默认智能体：

1. **初二数学助手**
   - 专门解答初二下学期数学问题的智能体
   - 覆盖代数、几何等知识点
   - 能力包括：代数运算、几何证明、问题解决、数学辅导

## 模块化设计

系统采用模块化设计，每个智能体都是一个独立的模块，可以轻松扩展和维护：

- **数学智能体模块** (`agents/math_agent.py`)：专门处理数学问题的智能体模块
- **调度器模块** (`agents/scheduler.py`)：负责解析用户意图并调度合适的智能体
- **工作智能体模块** (`agents/worker.py`)：处理具体任务执行
- **管理模块** (`agents/manager.py`)：负责智能体的注册、查询、更新等管理功能

其他模块通过引用方式使用数学智能体，保持了代码的低耦合和高内聚。

## 技术栈

- FastAPI: 用于构建Web API
- Pydantic: 数据验证和序列化
- Qwen2.5-32B: 大语言模型

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
uvicorn main:app --reload
```

## API接口文档

### 1. 智能体管理接口

#### 注册新智能体

- **URL**: `POST /api/v1/manager/agents/`
- **描述**: 注册一个新的智能体到系统中
- **请求体**:
  ```json
  {
    "name": "string",           // 智能体名称
    "description": "string",    // 智能体描述
    "agent_type": "scheduler|worker",  // 智能体类型
    "capabilities": ["string"]  // 智能体能力列表
  }
  ```
- **响应**:
  ```json
  {
    "name": "string",
    "description": "string",
    "agent_type": "scheduler|worker",
    "capabilities": ["string"],
    "id": "string",             // 智能体唯一标识
    "status": "active|inactive|offline",  // 智能体状态
    "created_at": "datetime",
    "last_heartbeat": "datetime"
  }
  ```

#### 获取智能体列表

- **URL**: `GET /api/v1/manager/agents/`
- **描述**: 获取系统中所有智能体的列表，支持按类型和状态过滤
- **参数**:
  - `agent_type` (可选): 过滤智能体类型 (scheduler|worker)
  - `status` (可选): 过滤智能体状态 (active|inactive|offline)
- **响应**: 智能体对象数组

#### 获取指定智能体

- **URL**: `GET /api/v1/manager/agents/{agent_id}`
- **描述**: 获取指定ID的智能体详细信息
- **参数**:
  - `agent_id`: 智能体唯一标识
- **响应**: 智能体对象

#### 更新智能体信息

- **URL**: `PUT /api/v1/manager/agents/{agent_id}`
- **描述**: 更新指定智能体的信息
- **参数**:
  - `agent_id`: 智能体唯一标识
- **请求体**:
  ```json
  {
    "name": "string",           // (可选) 智能体名称
    "description": "string",    // (可选) 智能体描述
    "capabilities": ["string"], // (可选) 智能体能力列表
    "status": "active|inactive|offline"  // (可选) 智能体状态
  }
  ```
- **响应**: 更新后的智能体对象

#### 注销智能体

- **URL**: `DELETE /api/v1/manager/agents/{agent_id}`
- **描述**: 从系统中移除指定的智能体
- **参数**:
  - `agent_id`: 智能体唯一标识
- **响应**:
  ```json
  {
    "message": "Agent unregistered successfully"
  }
  ```

#### 发送心跳

- **URL**: `POST /api/v1/manager/agents/{agent_id}/heartbeat`
- **描述**: 智能体发送心跳以表明其在线状态
- **参数**:
  - `agent_id`: 智能体唯一标识
- **请求体**:
  ```json
  {
    "agent_id": "string",       // 智能体ID
    "timestamp": "datetime"     // 心跳时间
  }
  ```
- **响应**:
  ```json
  {
    "message": "Heartbeat received"
  }
  ```

### 2. 调度智能体接口

#### 处理用户查询

- **URL**: `POST /api/v1/scheduler/process_query`
- **描述**: 接收用户自然语言查询，解析意图并返回需要调用的工作智能体列表
- **请求体**:
  ```json
  {
    "query": "string",          // 用户查询
    "context": {}               // (可选) 上下文信息
  }
  ```
- **响应**:
  ```json
  {
    "task_id": "string",        // 任务ID
    "target_agents": [          // 目标智能体列表
      {
        "id": "string",         // 智能体ID
        "name": "string",       // 智能体名称
        "description": "string" // 智能体描述
      }
    ],
    "response": "string"        // 响应内容
  }
  ```

当用户查询涉及数学相关内容时，系统会自动识别并返回初二数学助手智能体。

### 3. 工作智能体接口

#### 执行任务

- **URL**: `POST /api/v1/worker/execute/{agent_id}`
- **描述**: 在指定的工作智能体上执行任务
- **参数**:
  - `agent_id`: 智能体唯一标识
- **请求体**:
  ```json
  {
    "task_id": "string",        // 任务ID
    "input_data": {},           // 输入数据
    "metadata": {}              // (可选) 元数据
  }
  ```
- **响应**:
  ```json
  {
    "task_id": "string",        // 任务ID
    "agent_id": "string",       // 智能体ID
    "output_data": {},          // 输出数据
    "execution_time": 0.0,      // 执行时间(秒)
    "status": "string"          // 执行状态
  }
  ```

## 统一消息协议

系统使用基于JSON的统一消息协议，所有消息都遵循以下格式：

```json
{
  "id": "string",               // 消息唯一标识
  "source_agent_id": "string",  // 源智能体ID
  "target_agent_id": "string",  // 目标智能体ID
  "content": {},                // 消息内容
  "timestamp": "datetime",      // 消息时间戳
  "metadata": {}                // (可选) 消息元数据
}
```

## 并发处理

所有请求都支持并发执行，前端可以根据调度器返回的[target_agents](file:///d:/python_codes/agentManager/schemas/agent.py#L51-L51)列表并发调用各个工作智能体的执行接口。

## 错误处理

系统使用标准HTTP状态码表示请求结果：
- `200`: 请求成功
- `400`: 请求参数错误
- `404`: 资源未找到
- `500`: 服务器内部错误

详细的错误信息会在响应体的`detail`字段中提供。

## 配置

系统通过环境变量进行配置：
- `QWEN_API_KEY`: Qwen API密钥
- `QWEN_MODEL_NAME`: 使用的模型名称，默认为`qwen2.5-32b`
- `QWEN_API_BASE`: Qwen API基础URL（可选）

## 扩展新的智能体模块

要创建新的智能体模块，请按照以下步骤操作：

1. 在 `agents/` 目录下创建新的智能体文件，如 `new_agent.py`
2. 定义智能体配置和注册函数
3. 在系统启动时注册该智能体
4. 在调度器中添加对该智能体的识别逻辑
5. 在工作智能体中添加具体的任务处理逻辑