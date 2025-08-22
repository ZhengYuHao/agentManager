URL:106.227.68.33:8847 

#### 处理用户查询

- **URL**: `POST /api/v1/scheduler/process_query`
- **描述**: 接收用户自然语言查询，解析意图并返回需要调用的工作智能体列表
- **请求体**:
  ```json
  {
    "query": "string",          // 用户查询
    "session_id": "string",     // (可选) 会话ID
    "context": {}               // (可选) 上下文信息
  }
  ```
- **响应**:
  ```json
  {
    "task_id": "string",        // 任务ID
    "session_id": "string",     // 会话ID
    "target_agents": [          // 目标智能体列表
      {
        "id": "string",         // 智能体ID
        "name": "string",       // 智能体名称
        "description": "string", // 智能体描述
        "source": "internal|external" // 智能体来源
      }
    ],
    "response": "string"        // 响应内容
  }
  `

  ### 工作智能体接口

#### 执行任务

- **URL**: `POST /api/v1/worker/execute/{agent_id}`  这里的agent_id是动态的，根据实际智能体的ID来，也就是调用`POST /api/v1/scheduler/process_query`的target_agents列表中的ID
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

