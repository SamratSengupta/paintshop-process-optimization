from paintshop_constraints import *

class PaintshopReward:

    def __init__(self,paint_shop):
        self.paint_process_reward = 5
        self.idle_time_penalty = 5
        self.paint_completion_reward = 5
        self.constraint_violation_penalty = 25

    def calculate_reward(self, action_matrix, current_machines, next_machines,connectors):


       reward=0
       #step reward
        # 
        # 1.delta reward for each unit of paint processed 
        # 2.delta reward for unit of paint completed in distributor
        # 3.penalize for each unit of idle Time (all m/c).
        # 4.penalize for constraint violation ->
        #       i>both inp and oup connector set to 1 for tsd-mx-pk m/c (big penalty)
        # 

        del_paint_completed=0 ; del_idle_time_machines = []        
        del_paint_processed_machines= [] ; constraint_reward_machines=[]
        constraint_reward_machines=[]      

        for i,j in zip(current_machines,next_machines):
            del_idle_time = j.idle_time - i.idle_time
            del_idle_time_machines.append(del_idle_time)

            if i.type in ['TSD','MX','PR'] and j.type in ['TSD','MX','PR']:
                
                del_vol_processed = j.volume_processing - i.volume_processing
                del_paint_processed_machines.append(del_vol_processed)

            if i.type=='DST' and j.type=='DST':
                del_paint_completed = del_paint_completed + j.volume


        for act,connect in zip(action_matrix,connectors):
            src , dst = connect
            if int(act) == 1:                    
                src.outconnect = 1 ; dst.inconnect = 1
            elif int(act) == 0:
                src.outconnect = 0 ; dst.inconnect = 0

        for indx,machine in enumerate(self.get_all_machines()): 
                if machine.inconnect == 1 and machine.outconnect == 1:
                    constraint_reward_machines.append(self.constraint_violation_penalty)


        reward -= np.sum(constraint_reward_machines)

        reward += del_paint_completed * self.paint_completion_reward

        reward += np.sum(del_paint_processed_machines) * self.paint_process_reward

        reward -= np.sum(del_idle_time_machines) * self.idle_time_penalty

        return reward

       




        
       

        
         

        







        




        
        
            
       
       


        
        

       