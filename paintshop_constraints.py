## **** Machine Capacity and Operation Rules 

def check_capacity_constraint(machine, action):
    action_type, _, _, paint_color = action

    if action_type == 'start_fill' and machine.status == 'idle':
        projected_volume = machine.volume + machine.fill_rate
        if projected_volume > machine.capacity:
            return False  # Violates capacity constraint
    return True

def check_color_processing_constraint(machine, action):
    _, _, _, paint_color = action

    if machine.status == 'idle' and machine.volume == 0:
        return True  # Machine is empty, can process any color

    if machine.current_paint != paint_color:
        return False  # Attempting to process a different color without emptying

    return True

def check_operational_state_constraint(machine, action):
    action_type, _, _, _ = action

    if action_type == 'start_fill' and machine.status != 'idle':
        return False  # Cannot start filling unless machine is idle
    if action_type == 'start_empty' and machine.status != 'processing':
        return False  # Cannot start emptying unless machine is processing

    return True



def check_operational_time_constraint(machine):

    # For the operational time constraint, the logic is generally as follows:
    # If a machine is in a state (like processing, filling, or emptying) and the elapsed time in that state is less than
    # the required time for that state, the constraint is violated, and no new action should be allowed. In this case, return False.
    # If the elapsed time meets or exceeds the required time, the constraint is not violated, and it is permissible to
    # change the state or perform an action. Here, return True.


    if machine.status == 'processing' and machine.time_elapsed < machine.process_time:
            return False  
    elif machine.status == 'filling' and machine.time_elapsed < machine.fill_time:
            return False
    elif machine.status == 'emptying' and machine.time_elapsed < machine.empty_time:
            return False
    else:
            return True   


    # In above method,If the machine is still within its required processing time (machine.time_elapsed < machine.process_time),
    # the function returns False, indicating that the constraint is violated, and the machine should not change its state
    # or start a new operation. If the machine has completed its required processing time, the function returns True,
    # indicating that it's okay to proceed with a state change or a new operation.
    # This approach ensures that the machine operations adhere to the specified time constraints, 
    # adding realism and complexity to your simulation.



def check_sequential_flow(machine, action, all_machines):

    # **** Sequential Operational Flow Constraints.
    # To implement the Sequential Operational Flow constraints for the paint shop environment, 
    # we need to enforce that the processing flow strictly follows the order of TSD → MX → PR,
    # and that each Mixer (MX) interacts correctly with the Twin-Shaft Disruptor (TSD) and Packager (PR).
    # Let's create functions to validate these constraints.


    # Processing Flow Order: Ensure that the processing flow follows TSD → MX → PR.
    # Mixer Input/Output Restrictions: A Mixer can only receive input from a TSD and can only pass its output to a PR.
    # Additionally, a Mixer should interact with only one TSD and one PR at any given time.

    
    def get_connected_machines(machine, machine_type, all_machines):
        """ 
        Return a list of machines connected to the given machine that are of the specified type.
        """
        return [m for m in all_machines if m.type == machine_type and m.id in machine.connected_machines]

    action_type, machine_type, machine_id, _ = action

    # Constraint for TSD → MX → PR flow
    if machine_type == 'MX':
        if action_type == 'start_fill':
            # Check if any connected TSD is in 'processing' state
            if not any(ts.status == 'processing' for ts in get_connected_machines(machine, 'TSD', all_machines)):
                return False
        elif action_type == 'start_empty':
            # Check if any connected PR is in 'idle' state
            if not any(pr.status == 'idle' for pr in get_connected_machines(machine, 'PR', all_machines)):
                return False

    return True  # Flow is sequential and valid

    # The function check_sequential_flow ensures that the actions taken adhere to the required sequential operational flow of TSD → MX → PR.
    # The get_connected_machines helper function retrieves all machines of a specific type connected to a given machine, which is 
    # useful for checking the state of connected machines.This approach enforces that Mixers properly interact with 
    # Twin-Shaft Disruptors and Packagers according to the defined rules, adding a realistic operational constraint to your environment.
    # Integrating these constraints ensures that the agent learns to navigate the paint shop environment by respecting the necessary
    # sequential operational flows and machine interactions.




def check_for_overlapping_operations(machine_id, action, all_machines):
    """
    Check if the action causes overlapping operations within the same line of machines.
    :param machine_id: ID of the machine performing the action.
    :param action: The action being performed.
    :param all_machines: List of all machines in the environment.
    :param line_configurations: Dictionary mapping lines to their machine IDs.
    :return: True if there is an overlap violation, False otherwise.
    """

    # Define the line configurations for the paint shop environment
    line_configurations = {
        'Line1': ['M7', 'M8', 'M9', 'M10'],  # Machines in Line 1
        'Line2': ['M11', 'M12', 'M13', 'M14'],  # Machines in Line 2
        'Line3': ['M15', 'M16', 'M17', 'M18'],  # Machines in Line 3
        'Line4': ['M19', 'M20', 'M21', 'M22']   # Machines in Line 4
    }

    # The line_configurations dictionary maps each line to the IDs of the mixers it contains. 
    # This structure makes it easy to check if a specific mixer is part of a line and to enforce the rule
    # that only one mixer in a line can receive material at a time.
    # When implementing check_for_overlapping_operations, the function will use this configuration 
    # to determine which machines are in the same line and enforce the operational constraints accordingly.



    def find_machine_by_id(all_machines, machine_id):
        """ Return the machine object with the given ID. """
        return next((m for m in all_machines if m.id == machine_id), None)

    def find_machine_line(machine_id, line_configurations):
        """ Return the line to which the machine belongs. """
        for line, machines in line_configurations.items():
            if machine_id in machines:
                return line
        return None

    def is_conflicting_operation(action_type, other_machine):
        """
        Determine if the action conflicts with the operation of the other machine.
        For example, if two machines in the same line cannot fill simultaneously.
        """
        if action_type == 'start_fill' and other_machine.status == 'filling':
            return True
        return False

    action_type, _, _, _ = action
    target_machine = find_machine_by_id(all_machines, machine_id)

    if target_machine and target_machine.type == 'MX':
        # Identify the line of the target machine
        line_of_target = find_machine_line(target_machine.id, line_configurations)

        # Check for conflicting operations within the same line
        for line, machines in line_configurations.items():
            if line == line_of_target:
                for other_machine_id in machines:
                    if other_machine_id != machine_id:
                        other_machine = find_machine_by_id(all_machines, other_machine_id)
                        if is_conflicting_operation(action_type, other_machine):
                            return True
                        
    return False
    # The check_for_overlapping_operations function determines if there are any operational conflicts based on the type and status of machines, especially within the same line.
    # The find_machine_by_id and find_machine_line helper functions are used to identify machines and their corresponding lines.
    # You need to define line_configurations according to your environment's setup, mapping each line to the IDs of machines that belong to it.
    # By adding these checks, you ensure that the agent operating in the environment respects the operational constraints related to overlapping actions, critical for maintaining realistic and efficient workflow management in the paint shop simulation.


def evaluate_idle_time_and_efficiency(all_machines, orders_remaining):
    """
    Evaluate and apply rewards or penalties based on idle time and efficiency.

    :param all_machines: List of all machine objects in the environment.
    :param orders_remaining: Dictionary indicating the remaining volume of orders for each color.
    :return: A numeric reward or penalty value.
    """

    efficiency_reward = 0
    idle_penalty = 0
    idle_threshold = 10  # Define a threshold for idle time (e.g., 10 time units)

    for machine in all_machines:
        # Check if the machine is idle when there is work to be done
        if machine.status == 'idle' and orders_remaining[machine.paint_type] > 0:
            # Apply a penalty if the machine is idle for too long
            if machine.idle_time > idle_threshold:
                idle_penalty -= 1  # Apply a penalty for each idle machine

        # Reward efficiency: If a machine is actively processing and not idle
        if machine.status == 'processing':
            efficiency_reward += 1  # Reward for each actively processing machine

    # Combine rewards and penalties
    total_reward = efficiency_reward + idle_penalty
    return total_reward
    # Idle Time Check: The function iterates over all machines and checks if any machine is idle
    # when there is pending work (orders remaining). If a machine remains idle beyond the defined idle_threshold, 
    # a penalty is applied.   Efficiency Reward: Machines that are actively processing (not idle) contribute to a positive 
    # efficiency reward. This encourages the agent to keep machines busy and avoid bottlenecks.
    # Combining Rewards and Penalties: The final reward is a combination of efficiency rewards and idle penalties.
    # A higher reward is given for keeping machines active and processing, while penalties are incurred 
    # for machines that remain idle unnecessarily.


def evaluate_safety_and_integrity(all_machines):
    """
    Evaluate actions for safety and operational integrity.

    :param all_machines: List of all machine objects in the environment.
    :return: A numeric reward or penalty value based on safety and operational integrity.
    """
    safety_penalty = 0
    integrity_reward = 0
    penalty_value = -5  # Define the penalty value for safety violations
    reward_value = 2    # Define the reward value for maintaining operational integrity

    for machine in all_machines:
        # Check for overfilling violation
        if machine.volume > machine.capacity:
            safety_penalty += penalty_value

        # Check for premature processing (processing before filling up to full capacity)
        if machine.status == 'processing' and machine.volume < machine.capacity:
            safety_penalty += penalty_value

        # Reward for maintaining operational integrity (adhering to machine capacities and processing times)
        if machine.status == 'processing' and machine.volume == machine.capacity and machine.time_elapsed >= machine.process_time:
            integrity_reward += reward_value

    total_reward = integrity_reward + safety_penalty
    return total_reward

    # Explanation
    # Safety Checks: The function iterates over all machines and checks for safety violations like overfilling or premature processing. Penalties are applied for each violation.
    # Operational Integrity: Machines that are processing at full capacity and have completed their required processing time without safety violations contribute to an operational integrity reward.
    # Combining Rewards and Penalties: The final reward is a combination of the integrity rewards and safety penalties.




def evaluate_order_progress(orders_initial, orders_remaining):


    def calculate_milestone_reward(progress, milestones, color):
        """
        Calculate the reward for achieving milestones for a specific color order.

        :param progress: The completion progress of the order (0 to 1).
        :param milestones: List of milestones to check against.
        :param color: The color of the paint order.
        :return: Reward for achieving milestones.
        """
        milestone_reward = 10  # Define the reward for achieving each milestone
        color_reward = {'R': 5, 'Y': 5, 'W': 5}  # Specific rewards for each color
        total_reward = 0

        for milestone in milestones:
            if progress >= milestone:
                total_reward += milestone_reward + color_reward.get(color, 0)

        return total_reward
    """
    Evaluate the progress of fulfilling paint orders and calculate rewards based on milestones achieved.

    :param orders_initial: Initial volume of orders for each paint color.
    :param orders_remaining: Current remaining volume of orders for each paint color.
    :return: A numeric reward based on order completion and milestones achieved.
    """
    reward = 0
    milestones = [0.25, 0.5, 0.75]  # Define milestones

    for color, initial_volume in orders_initial.items():
        if initial_volume > 0:
            progress = (initial_volume - orders_remaining[color]) / initial_volume
            reward += calculate_milestone_reward(progress, milestones, color)

    return reward