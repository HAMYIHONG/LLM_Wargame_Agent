"""Run some games in some scenarios locally.

This is the correct entry to start the program.
To test your agent, the major modifications you need to make are:
1. import your own agent class (you definitely know where it is)
2. instantiate your agent and its opponent (replace the Agent below)

The code looks like:

from ai.agent import Agent

red = Agent()
blue = DemoAgent()
"""
import json
import pickle
import time
import zipfile
import os
import numpy
import traceback  # 用于获取异常信息

from ai import Agent
from ai_LLM import Agent as Agent_LLM
from ai_LLM import reflection, conversation_history

from train_env import TrainEnv

RED, BLUE, GREEN = 0, 1, -1


def main():
    run_in_single_agent_mode()
    # run_in_multi_agents_mode()


def run_in_single_agent_mode():
    """
    run demo in single agent mode
    """
    print("running in single agent mode...")
    # instantiate agents and env
    red1 = Agent_LLM()
    blue1 = Agent()
    env1 = TrainEnv()
    begin = time.time()
    
    '''
    # get data ready, data comes from local files, change the scenarios and maps here
    # 此处已经更改为高原通道分队夺控战斗的想定和地图
    with open("Data/scenarios/e1.json", encoding='utf8') as f:
        scenario_data = json.load(f)
    with open("Data/maps/mini1/basic.json", encoding='utf8') as f:
        basic_data = json.load(f)        
    with open('Data/maps/mini1/cost.pickle', 'rb') as file:
        cost_data = pickle.load(file)
    see_data = numpy.load("Data/maps/mini1/see.npz")['data']
    '''

    with open("Data/scenarios/2010211129.json", encoding='utf8') as f:
        scenario_data = json.load(f)
    with open("Data/maps/map_29/basic.json", encoding='utf8') as f:
        basic_data = json.load(f)        
    with open('Data/maps/map_29/cost.pickle', 'rb') as file:
        cost_data = pickle.load(file)
    see_data = numpy.load("Data/maps/map_29/29see.npz")['data']


    # varialbe to build replay
    all_states = []
    red_states = []

    # player setup info
    player_info = [{
        "seat": 1,
        "faction": 0,
        "role": 1,
        "user_name": "DS",
        "user_id": 0
    },
    {
        "seat": 11,
        "faction": 1,
        "role": 1,
        "user_name": "demo",
        "user_id": 0
    }]

    # env setup info
    env_step_info = {
        "scenario_data": scenario_data,
        "basic_data": basic_data,
        "cost_data": cost_data,
        "see_data": see_data,
        "player_info": player_info
    }

    # setup env
    state = env1.setup(env_step_info)
    all_states.append(state[GREEN])
    red_states.append(state[RED])
    print("Environment is ready.")

    # setup AIs
    red1.setup(
        {
            "scenario": scenario_data,
            "basic_data": basic_data,
            "cost_data": cost_data,
            "see_data": see_data,
            "seat": 1,
            "faction": 0,
            "role": 0,
            "user_name": "demo",
            "user_id": 0,
            "state": state,
        }
    )

    blue1.setup(
        {
            "scenario": scenario_data,
            "basic_data": basic_data,
            "cost_data": cost_data,
            "see_data": see_data,
            "seat": 11,
            "faction": 1,
            "role": 0,
            "user_name": "demo",
            "user_id": 0,
            "state": state,
        }
    )
    print("agents are ready.")

    # loop until the end of game
    print("steping")
    done = False
    try:
        while not done: 
            ## 当在部署阶段时，应该要生成部署阶段的COA，以及部署阶段的命令
            actions = []
            try:
                actions += red1.step(state[RED])
            except Exception as e:
                print(f"Error occurred in red1.step: {e}")
                traceback.print_exc()  # 打印详细的异常信息
                break  # 出现异常时退出循环
            actions += blue1.step(state[BLUE])
            state, done = env1.step(actions)
            all_states.append(state[GREEN])
            red_states.append(state[RED])

    except Exception as e:
        print(f"Error occurred in env.step: {e}")
        traceback.print_exc()  # 打印详细的异常信息
    

    env1.reset()
    red1.reset()
    blue1.reset()

    print(f"Total time: {time.time() - begin:.3f}s")
    
    # 生成反思内容
    print("Now let's begin to do some analysis......")
    memory = reflection(all_states)
    memory_file = f"logs/memories/reflection_{begin}.json"
    with open(memory_file, 'w') as f:
        f.write(to_json_string(memory, indent=4))

    conversation_history_file = f"logs/full_conversation/conversation_history_{begin}.json"
    with open(conversation_history_file, 'w') as f:
        f.write(to_json_string(conversation_history, indent=4))

    # save replay
    zip_name = f"logs/replays/replay_{begin}.zip"
    zip_red_name = f"logs/replays/replay_red_{begin}.zip"
    if not os.path.exists("logs/replays/"):
        os.makedirs("logs/replays/")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for i, ob in enumerate(all_states):
            data = json.dumps(ob, ensure_ascii=False, separators=(",", ":"))
            z.writestr(f"{begin}/{i}", data)

    with zipfile.ZipFile(zip_red_name, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for i, ob in enumerate(red_states):
            data = json.dumps(ob, ensure_ascii=False, separators=(",", ":"))
            z.writestr(f"{begin}/{i}", data)
    ## 以下是对复盘文件的解压、抽取以及分析
    ## 这部分后续还可以优化 其实不需要解压 只从all_states中抽取内容并反思即可


def to_json_string(o, indent=None):
    return json.dumps(o, ensure_ascii=False, indent=indent, separators=(',', ':'))


def run_in_multi_agents_mode():
    """
    run demo in multi agent mode
    """
    print("running in multi agent mode...")
    # instantiate agents and env
    red1 = Agent()
    red2 = Agent()
    red3 = Agent()
    blue1 = Agent()
    blue2 = Agent()
    blue3 = Agent()
    env1 = TrainEnv()
    begin = time.time()

# get data ready, data can from files, web, or any other sources
    with open("Data/scenarios/2010211129.json", encoding='utf8') as f:
        scenario_data = json.load(f)
    with open("Data/maps/map_43/basic.json", encoding='utf8') as f:
        basic_data = json.load(f)
    with open('Data/maps/map_43/cost.pickle', 'rb') as file:
        cost_data = pickle.load(file)
    see_data = numpy.load("Data/maps/map_43/43see.npz")['data']

    # varialbe to build replay
    all_states = []

    # player setup info
    player_info = [{
        "seat": 1,
        "faction": 0,
        "role": 1,
        "user_name": "red1",
        "user_id": 1
    },
    {
        "seat": 2,
        "faction": 0,
        "role": 0,
        "user_name": "red2",
        "user_id": 2
    },
    {
        "seat": 3,
        "faction": 0,
        "role": 0,
        "user_name": "red3",
        "user_id": 3
    },
    {
        "seat": 11,
        "faction": 1,
        "role": 1,
        "user_name": "blue1",
        "user_id": 11
    },
    {
        "seat": 12,
        "faction": 1,
        "role": 0,
        "user_name": "blue2",
        "user_id": 12
    },
    {
        "seat": 13,
        "faction": 1,
        "role": 0,
        "user_name": "blue3",
        "user_id": 13
    }]

    # env setup info
    env_step_info = {
        "scenario_data": scenario_data,
        "basic_data": basic_data,
        "cost_data": cost_data,
        "see_data": see_data,
        "player_info": player_info
    }

    # setup env
    state = env1.setup(env_step_info)
    all_states.append(state[GREEN])
    print("Environment is ready.")

    # setup AIs
    red1.setup(
        {
            "scenario": scenario_data,
            "basic_data": basic_data,
            "cost_data": cost_data,
            "see_data": see_data,
            "seat": 1,
            "faction": 0,
            "role": 1,
            "user_name": "red1",
            "user_id": 1,
            "state": state,
        }
    )
    red2.setup(
        {
            "scenario": scenario_data,
            "basic_data": basic_data,
            "cost_data": cost_data,
            "see_data": see_data,
            "seat": 2,
            "faction": 0,
            "role": 0,
            "user_name": "red2",
            "user_id": 2,
            "state": state,
        }
    )
    red3.setup(
        {
            "scenario": scenario_data,
            "basic_data": basic_data,
            "cost_data": cost_data,
            "see_data": see_data,
            "seat": 3,
            "faction": 0,
            "role": 0,
            "user_name": "red3",
            "user_id": 3,
            "state": state,
        }
    )
    blue1.setup(
        {
            "scenario": scenario_data,
            "basic_data": basic_data,
            "cost_data": cost_data,
            "see_data": see_data,
            "seat": 11,
            "faction": 1,
            "role": 1,
            "user_name": "blue1",
            "user_id": 11,
            "state": state,
        }
    )
    blue2.setup(
        {
            "scenario": scenario_data,
            "basic_data": basic_data,
            "cost_data": cost_data,
            "see_data": see_data,
            "seat": 12,
            "faction": 1,
            "role": 0,
            "user_name": "blue2",
            "user_id": 12,
            "state": state,
        }
    )
    blue3.setup(
        {
            "scenario": scenario_data,
            "basic_data": basic_data,
            "cost_data": cost_data,
            "see_data": see_data,
            "seat": 13,
            "faction": 1,
            "role": 0,
            "user_name": "blue3",
            "user_id": 13,
            "state": state,
        }
    )
    print("agents are ready.")

    # loop until the end of game
    print("steping")
    done = False
    while not done:
        actions = []
        actions += red1.step(state[RED])
        actions += red2.step(state[RED])
        actions += red3.step(state[RED])
        actions += blue1.step(state[BLUE])
        actions += blue2.step(state[BLUE])
        actions += blue3.step(state[BLUE])
        state, done = env1.step(actions)
        all_states.append(state[GREEN])

    env1.reset()
    red1.reset()
    red2.reset()
    red3.reset()
    blue1.reset()
    blue2.reset()
    blue3.reset()

    print(f"Total time: {time.time() - begin:.3f}s")

    # save replay
    zip_name = f"logs/replays/replay_{begin}.zip"
    if not os.path.exists("logs/replays/"):
        os.makedirs("logs/replays/")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for i, ob in enumerate(all_states):
            data = json.dumps(ob, ensure_ascii=False, separators=(",", ":"))
            z.writestr(f"{begin}/{i}", data)

if __name__ == "__main__":
    main()
