```mermaid
graph TD
    subgraph S1["3.2.1 兵棋环境与态势生成"]
        A[兵棋原始数据] --> B{态势数据结构化};
        B --> C{态势语义转换};
        C --> D[态势信息凝练与压缩<br>(大模型提取关键态势)];
    end

    subgraph S2["3.2.2 基于MDMP流程的多智能体作战计划生成模型"]
        D --> E[作战任务指令<br>地形分析与约束];
        E --> F{MDMP多智能体协同讨论};
        F -- "由情报参谋智能体" --> G[敌情分析报告];
        F -- "由作战参谋智能体" --> H[COA生成与初步评估<br>(生成多套方案，暂无兵棋推演接口)];
        H --> I{指挥官智能体决策与批准};
        I --> J[生成结构化作战计划];
    end

    subgraph S3["3.2.3 基于任务驱动的战术动作执行框架"]
        J --> K{作战计划任务分解<br>(TaskGroupNode)};
        K -- "拆解为" --> L[单元级动作命令];
        L --> M{算子任务管理器<br>(管理单算子TaskList)};
        M --> N{群队任务管理器<br>(管理GroupTaskList，协调多算子)};
        N --> O[兵棋系统中的红方单位动作下达];
        O --> P[兵棋推演与态势更新];
    end

    subgraph S4["决策与反馈闭环"]
        P --> Q{特定触发条件判断<br>(时间/兵力损失等)};
        Q -- "若满足，触发" --> F;
        Q -- "若不满足" --> O;
    end

    style S1 fill:#f9f,stroke:#333,stroke-width:2px;
    style S2 fill:#dfd,stroke:#333,stroke-width:2px;
    style S3 fill:#ddf,stroke:#333,stroke-width:2px;
    style S4 fill:#fdf,stroke:#333,stroke-width:2px;

    D -- "输入" --> F;
    J -- "输入" --> K;
    P -- "反馈" --> D;
