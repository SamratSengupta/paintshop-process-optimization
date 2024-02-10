
import pandas as pd
import numpy as np
import gym
from gym import spaces
from paintshop_setup import PaintShop, Machine
from paintshop_rewards import PaintshopReward

class PaintShopState:
    def __init__(self, paint_shop):
        self.paint_shop = paint_shop 

    def get_machine_state(self, machine):
        # Assuming Machine class has methods to get the current status, volume, and color
        status_code = int(machine.get_status_code())
        volume = float(machine.volume)
        paint_code = int(machine.get_paint_code())
        machine_type_code = int(machine.get_machine_type_code())
        idle_time = float(machine.idle_time)
        return [machine_type_code, paint_code, status_code, volume,idle_time]     

    def get_current_state(self):
        machine_lst = []
        for indx,machine in enumerate(self.paint_shop.get_all_machines()):
            machine_lst.append(self.get_machine_state(machine))
        return np.array(machine_lst) 


    
   

class PaintShopEnv(gym.Env):
    def __init__(self,order_data_path):

        super(PaintShopEnv, self).__init__()

        #initialize paintshop 
        self.paint_shop = PaintShop(order_data_path)
        #create state from initialized order and paintshop
        #initialize paintshop 1st order
        self.order_num=0         
        #initialize reward object
        self.reward_computer= PaintshopReward(self.paint_shop)

        # Define action and observation space
        # machinetype , painttype, status, volume ,idle_time in order     

        print('connector length :' , len(self.paint_shop.connectors)) 

        self.action_space = spaces.MultiBinary(len(self.paint_shop.connectors))
        self.observation_space = self.initialize_observation_space()        
        print('obsrvation space dims :: ',self.observation_space.shape)

    def initialize_observation_space(self):

        low_single_machine = np.array([0, 0, 0, 0, 0])
        # Define the upper bounds for each dimension of a single machine's observation
        high_single_machine = np.array([4, 2, 3, 10000, 480])
        # Repeat these bounds for all machines to create the full observation space bounds
        low = np.tile(low_single_machine, (self.paint_shop.num_machines, 1))
        high = np.tile(high_single_machine, (self.paint_shop.num_machines, 1))

        return spaces.Box(low=low, high=high, dtype=np.float32)

    
    # mandatory
    def reset(self):
        self.paint_shop.reset_machines()
        self.paint_shop.initialize_order(self.order_num) 
        self.paintshop_state = PaintShopState(self.paint_shop)
        observation = self.paintshop_state.get_current_state()
        print('paint shop state dim :: ',observation)
        return observation

    # mandatory
    def step(self, action):

        # Implement the logic to handle an action
        # Update the state
        # Calculate reward
        # Check if the episode is done
        # Return observation, reward, done, info

        curr_machines = self.paint_shop.get_all_machines()


        ## capture output action from policy in a matrix 
        action_matrix = action

        ### state change based on action ###       
        self.apply_action(action_matrix)       
        next_state = np.array(self.paintshop_state.get_current_state())

        ### calculate rewards based on transition to new state ###

        next_machines = self.paint_shop.get_all_machines()


        step_reward = self.reward_computer.calculate_reward(action_matrix, current_machines, next_machines,self.paint_shop.connectors)
        

       ### formulate end of episode logic

        done = False

        return next_state, step_reward, done, {} 
        
    

    ### handle change of state based on action taken ###
    def apply_action(self, action_matrix):

        print('apply action ' , action_matrix) 
        for connector, act in zip(self.paint_shop.connectors,action_matrix):
            ### Status , volume, idle , time elapsed in current status 
            ### For Reservoir and TSD connection
            print("action", act)
            if act==1.0:
                if connector[0].type == 'RSV': #####REs - TSD
                    if connector[0].status == 'idle' and connector[1].status != 'processing' and connector[1] != 'emptying':
                        connector[0].status = 'emptying' 
                        connector[1].status = 'filling'
                        # connector[1].volume_processing = connector[0].volume - connector[1].inflow_rate
                        # connector[0].volume_processing = connector[0].volume - connector[0].outflow_rate
                        connector[0].volume = connector[0].volume - connector[0].outflow_rate
                        connector[1].volume += connector[0].outflow_rate

                    elif connector[0].status == 'emptying':
                        if (connector[1].status == 'filling' or  connector[1].status == 'idle') & (connector[1].volume < connector[1].capacity) :
                            connector[1].status = 'filling'                                            
                            connector[0].status = 'emptying'
                            connector[1].volume += connector[0].outflow_rate
                            connector[0].volume = connector[0].volume - connector[0].outflow_rate                

                    elif (connector[1].volume == connector[1].capacity):
                        connector[1].volume_processing = connector[1].volume_processing - connector[1].inflow_rate
                        if connector[1].volume_processing == 0:
                            connector[1].status = 'idle'
                            connector[0].status = 'idle'
                            connector[1].volume_status = 'full'
                        else:
                            connector[1].status = 'processing'
                            connector[0].status = 'idle'

                ## For TSD connection and Mixer 
                elif connector[0].type == 'TSD' :  ## TSD -- MI
                    if connector[0].status == 'idle'  and (connector[1].status != 'processing' or connector[1].status != 'emptying') and connector[0].volume_status == 'full' :
                        connector[0].status = 'emptying' 
                        connector[1].status = 'filling'
                        connector[0].volume = connector[0].volume - connector[0].outflow_rate
                        connector[1].volume += connector[0].outflow_rate
                        
                    elif connector[0].status == 'emptying':
                        if (connector[1].status == 'filling' or  connector[1].status == 'idle') & (connector[1].volume < connector[1].capacity) :
                            connector[1].status = 'filling'                                            
                            connector[0].status = 'emptying'
                            connector[1].volume += connector[0].outflow_rate
                            connector[0].volume = connector[0].volume - connector[0].outflow_rate


                    elif (connector[1].volume == connector[1].capacity):
                        connector[1].volume_processing = connector[1].volume_processing - connector[1].inflow_rate
                        if connector[1].volume_processing == 0:
                            connector[1].status = 'idle'
                            connector[0].status = 'idle'
                            connector[1].volume_status = 'full'
                        else:
                            connector[1].status = 'processing'
                            connector[0].status = 'idle'        

                ### For Mixer connection and Packaging
                elif connector[0].type == 'MX' :  ## MIX -- Packaging
                    if connector[0].status == 'idle'  and (connector[1].status != 'processing' or connector[1].status != 'emptying') and connector[0].volume_status == 'full':
                        connector[0].status = 'emptying' 
                        connector[1].status = 'filling'
                        connector[0].volume = connector[0].volume - connector[0].outflow_rate
                        connector[1].volume += connector[0].outflow_rate
    

                    elif connector[0].status == 'emptying':
                        if (connector[1].status == 'filling' or  connector[1].status == 'idle') & (connector[1].volume < connector[1].capacity) :
                            connector[1].status = 'filling'                                            
                            connector[0].status = 'emptying'
                            connector[1].volume += connector[0].outflow_rate
                            connector[0].volume = connector[0].volume - connector[0].outflow_rate

                    elif (connector[1].volume == connector[1].capacity):
                        connector[1].volume_processing = connector[1].volume_processing - connector[1].inflow_rate
                        if connector[1].volume_processing == 0:
                            connector[1].status = 'idle'
                            connector[0].status = 'idle'
                            connector[1].volume_status = 'full'
                        else:
                            connector[1].status = 'processing'
                            connector[0].status = 'idle'


                elif connector[0].type == 'PR' :  ## PACK -- Distribution
                    if connector[0].status == 'idle' and connector[0].volume_status == 'full':
                        connector[0].status = 'emptying' 
                        connector[1].status = 'filling'
                        connector[0].volume = connector[0].volume - connector[0].outflow_rate
                        connector[1].volume += connector[0].outflow_rate

                    elif connector[0].status == 'emptying':
                        if connector[1].volume < connector[1].capacity :
                            connector[1].volume += connector[0].outflow_rate
                            connector[0].status ='emptying'

                    elif (connector[1].volume == connector[1].capacity):
                        connector[1].volume_processing = connector[1].volume_processing - connector[1].inflow_rate
                        if connector[1].volume_processing == 0:
                            connector[0].status = 'idle'
                        else:
                            connector[0].status = 'emptying'           
                 
                        
            elif act == 0:
                connector[0].idle_time += 1
                connector[1].idle_time += 1   


        
       
       
    def calculate_reward(self, action,state,next_state):
        # Implement reward calculation logic
        # Example: Reward could be based on efficiency, adherence to constraints, etc.
        # ... [reward calculation logic here] ...
        reward=self.reward_computer.calculate_reward(action,state,next_state)
        return reward

    
    # mandatory 
    def render(self, mode='human'):
        # Render the environment, if needed
        pass
    
    # mandataory
    def close(self):
        # Close and clean up the environment, if needed
        pass