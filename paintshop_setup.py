import pandas as pd
import ast
class Machine:
    def __init__(self, id, type, capacity,process_rate, inflow_rate, outflow_rate):

        self.id = id

        # these are the intrinsic properties of the machines and not used directly in state
        self.capacity = capacity
        self.process_rate = process_rate
        self.inflow_rate = inflow_rate
        self.outflow_rate = outflow_rate  

        # inconnect and outconnect 
        self.inconnect=0; self.outconnect=0     
        

        #this is a constant variable for a machine but used as an input to state
        self.type = type
        self.paint_type = 'NA'   

        #these properties of the machines will be used for state configuration and are variables
        
        self.volume = 0 # initialize volume to be processed
        self.status = 'idle'  # Assuming default status is 'idle'  ['idle->0,'processing'->1,'filling'->2,'emptying'->3]     
        self.idle_time = 0  # Initialize idle time


        # To determine the volume processed in the machine
        self.volume_processing = 0
        self.volume_status = 'NA'

        #this determines next machine state
        self.connected_machines = []

        #this variable is adjusted in each step to keep track of state change operation
        #but not used directly in state 

        self.cur_state_time=0 # Initialize time elapsed in current status

        #this determines whether the connection to its next machine is on-1 or off -0
        self.out_flow_conector=0

    # Getters for encoded variables
        
    def get_status_code(self):
        status_code = {'idle':0,'processing':1,'filling':2,'emptying':3}[self.status]
        return status_code
    
    def get_paint_code(self):
        paint_code = {'R':0,'Y':1,'W':2}[self.paint_type]
        return paint_code 
    
    def get_machine_type_code(self):
        machine_type_code = {'RSV':0,'TSD':1,'MX':2,'PR':3,'DST':4}[self.type]
        return machine_type_code

    
    def connect_machine(self, machine):
        if machine not in self.connected_machines:
            self.connected_machines.append(machine)


    ## update machine state variables as state changes in env
    def update_machine_state(self):
        print('will start coding ....')
    


class PaintShop:
    def __init__(self,order_data_path):

        #please note inflow/outflow rate are given as time taken to fill per minute 

        #initialize all macghines as per id, type, capacity,process_rate, inflow_rate, outflow_rate
        self.reservoirs = [Machine(f"M{i}", "RSV", 10000, 0, 0, 20) for i in range(4)]
        self.tsd_machines = [Machine(f"M{i}", "TSD", 120, 60, 20, 15) for i in range(4)]
        self.mx_machines = [Machine(f"M{i+7}", "MX", 180, 45, 15, 10) for i in range(8)]
        self.pr_machines = [Machine(f"M{i+23}", "PR", 200, 20, 10, 5) for i in range(4)]
        self.distributors=[Machine(f"M{i+23}", "DST", 10000, 0, 5, 0) for i in range(3)]

        #create a list containing conectors to machines in an ordered way
        self.connectors = []
       
        #set paint type to each machines
        self.configure_machines()

        #set connections or machine linkages
        self.connect_machines()

        #get total machines
        self.num_machines=len(self.get_all_machines())

        #initialize paintshop order
        self.orders = pd.read_csv(order_data_path)

        
        

    def configure_machines(self):

        #configure reservoirs 
        
        self.reservoirs[0].paint_type='R'
        self.reservoirs[1].paint_type='Y'
        self.reservoirs[2].paint_type='W'
        self.reservoirs[3].paint_type='W'

        # Configure TSD machines
        self.tsd_machines[0].paint_type='R'
        self.tsd_machines[1].paint_type='Y'
        self.tsd_machines[2].paint_type='W'
        self.tsd_machines[3].paint_type='W'        

        # Configure MX machines
        
        self.mx_machines[0].paint_type='R'
        self.mx_machines[1].paint_type='R'
        self.mx_machines[2].paint_type='Y'
        self.mx_machines[3].paint_type='Y'

        self.mx_machines[4].paint_type='W'
        self.mx_machines[5].paint_type='W'
        self.mx_machines[6].paint_type='W'
        self.mx_machines[7].paint_type='W'   
        

        # Configure PR machines

        self.pr_machines[0].paint_type='R'
        self.pr_machines[1].paint_type='Y'
        self.pr_machines[2].paint_type='W'
        self.pr_machines[3].paint_type='W'


        #Configure distributor machines

        self.distributors[0].paint_type='R'
        self.distributors[1].paint_type='Y'
        self.distributors[2].paint_type='W'

    def connect_machines(self):         

        #connect red reservoir with red tsd
        self.reservoirs[0].connect_machine(self.tsd_machines[0])
        self.connectors.append((self.reservoirs[0],self.tsd_machines[0]))

        #connect yellow reservoir with yellow tsd
        self.reservoirs[1].connect_machine(self.tsd_machines[1])
        self.connectors.append((self.reservoirs[1],self.tsd_machines[1]))

        #connect white reservoir with white tsd
        self.reservoirs[2].connect_machine(self.tsd_machines[2])
        self.connectors.append((self.reservoirs[2],self.tsd_machines[2]))

        self.reservoirs[3].connect_machine(self.tsd_machines[3])
        self.connectors.append((self.reservoirs[3],self.tsd_machines[3]))
        

        ##connect red tsd with red mixer
        self.tsd_machines[0].connect_machine(self.mx_machines[0])
        self.connectors.append((self.tsd_machines[0],self.mx_machines[0]))

        self.tsd_machines[0].connect_machine(self.mx_machines[1])
        self.connectors.append((self.tsd_machines[0],self.mx_machines[1]))


        ##connect yellow tsd with yellow mixer
        self.tsd_machines[1].connect_machine(self.mx_machines[2])
        self.connectors.append((self.tsd_machines[1],self.mx_machines[2]))

        self.tsd_machines[1].connect_machine(self.mx_machines[3])
        self.connectors.append((self.tsd_machines[1],self.mx_machines[3]))


        ##connect white tsd with white mixer       
        self.tsd_machines[2].connect_machine(self.mx_machines[4])
        self.connectors.append((self.tsd_machines[2],self.mx_machines[4]))

        self.tsd_machines[2].connect_machine(self.mx_machines[5])
        self.connectors.append((self.tsd_machines[2],self.mx_machines[5]))

        self.tsd_machines[3].connect_machine(self.mx_machines[6])
        self.connectors.append((self.tsd_machines[3],self.mx_machines[6]))

        self.tsd_machines[3].connect_machine(self.mx_machines[7])
        self.connectors.append((self.tsd_machines[3],self.mx_machines[7]))


        ##connect red mixer with red packer
        self.mx_machines[0].connect_machine(self.pr_machines[0])
        self.connectors.append((self.mx_machines[0],self.pr_machines[0]))


        self.mx_machines[1].connect_machine(self.pr_machines[0])
        self.connectors.append((self.mx_machines[1],self.pr_machines[0]))


        ##connect yellow mixer with yellow packer
        self.mx_machines[2].connect_machine(self.pr_machines[1])
        self.connectors.append((self.mx_machines[2],self.pr_machines[1]))


        self.mx_machines[3].connect_machine(self.pr_machines[1])
        self.connectors.append((self.mx_machines[3],self.pr_machines[1]))
        

        ##connect white mixer with white packer 
        self.mx_machines[4].connect_machine(self.pr_machines[2])
        self.connectors.append((self.mx_machines[4],self.pr_machines[2]))


        self.mx_machines[5].connect_machine(self.pr_machines[2])
        self.connectors.append((self.mx_machines[5],self.pr_machines[2]))


        self.mx_machines[6].connect_machine(self.pr_machines[3])
        self.connectors.append((self.mx_machines[6],self.pr_machines[3]))


        self.mx_machines[7].connect_machine(self.pr_machines[3]) 
        self.connectors.append((self.mx_machines[7],self.pr_machines[3]))


        ## connect red packer to red  distributor 
        self.pr_machines[0].connect_machine(self.distributors[0])
        self.connectors.append((self.pr_machines[0],self.distributors[0]))


        ## connect yellow packer to yellow distributor
        self.pr_machines[1].connect_machine(self.distributors[1])
        self.connectors.append((self.pr_machines[1],self.distributors[1]))


        ## connect white packers to white distributor
        self.pr_machines[2].connect_machine(self.distributors[2])
        self.connectors.append((self.pr_machines[2],self.distributors[2]))

        self.pr_machines[3].connect_machine(self.distributors[2])
        self.connectors.append((self.pr_machines[3],self.distributors[2]))

    

    def is_feasible_connection(self, source_machine, target_machine):
        """Check if the connection between two machines is feasible."""
        if target_machine in source_machine.connected_machines:
            return True
        else:
            return False


    def reset_machines(self):
        
        for indx,machine in enumerate(self.get_all_machines()):
            machine.status='idle'
            machine.idle_time=0
            machine.volume=0
            machine.cur_state_time=0
            machine.out_flow_conector=0


    def initialize_order(self,row_num):

        ## we assume initially all tsd's are filled , from connected tank and for this
        row_order = self.orders.loc[row_num]
               
        self.reservoirs[0].volume=float(row_order['Red'])
        self.reservoirs[1].volume=float(row_order['Yellow'])

        row_white = ast.literal_eval(row_order['White'])
        self.reservoirs[2].volume=float(row_white[0])
        self.reservoirs[3].volume=float(row_white[1])
    
    
    def get_all_machines(self):
        # Combine all machines into one list and return
        return self.reservoirs + self.tsd_machines + self.mx_machines + self.pr_machines + self.distributors
    
    
    def calculate_time_for_machines(self, machines, volume):
        """
        Calculate the total time required for a set of machines to process the given volume.
        Assumes that machines of the same type can work in parallel.
        """
        if not machines:
            return 0

        # Calculate the number of batches needed for one machine
        batches = -(-volume // machines[0].capacity)  # Ceiling division

        # Calculate time for one batch cycle
        batch_time = (machines[0].capacity / machines[0].inflow_rate) + \
                     (machines[0].capacity / machines[0].process_rate) + \
                     (machines[0].capacity / machines[0].outflow_rate)

        # Total time is number of batches multiplied by time per batch
        return batches * batch_time
    
    def calculate_processing_time(self, order):
        """
        Calculate the total time required for processing the given order.
        The order is a dictionary with keys 'R', 'Y', 'W' representing the volume of each paint color.
        """
        total_time = 0

        for color, volume in order.items():
            # Filter machines that can process the current color
            tsd_machines = [m for m in self.tsd_machines if m.can_process_paint(color)]
            mx_machines = [m for m in self.mx_machines if m.can_process_paint(color)]
            pr_machines = [m for m in self.pr_machines if m.can_process_paint(color)]

            tsd_time = self.calculate_time_for_machines(tsd_machines, volume)
            mx_time = self.calculate_time_for_machines(mx_machines, volume)
            pr_time = self.calculate_time_for_machines(pr_machines, volume)

            max_time_for_color = max(tsd_time, mx_time, pr_time)
            total_time = max(total_time, max_time_for_color)

        return total_time


# #Instantiate the PaintShop
# paint_shop = PaintShop(order_data_path='C:/work/RL-Strategic/paint-shop-optimization/data/order.csv')

# # Example usage: Check if a specific TSD can process red paint
# print("Can M1 process red paint?", paint_shop.tsd_machines[1].can_process_paint('R'))
# # Check if a connection is feasible
# print("Can M0 (RSV) feed M4 (TSD)?", paint_shop.is_feasible_connection(paint_shop.reservoirs[0], paint_shop.tsd_machines[0]))

# # Test the feasibility

# order = {'R': 500, 'Y': 700, 'W': 1000}  # Order in liters

# total_processing_time = paint_shop.calculate_processing_time(order)
# shift_length = 480  # 8 hours in minutes

# is_feasible = total_processing_time <= shift_length
# print("Can the order be completed in an 8-hour shift?", "Yes" if is_feasible else "No")