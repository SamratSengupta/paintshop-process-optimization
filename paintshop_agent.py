import torch
import torch.nn as nn
from stable_baselines3 import PPO
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
import gym

class CustomNetwork(BaseFeaturesExtractor):
    def __init__(self, observation_space, features_dim):
        super(CustomNetwork, self).__init__(observation_space,features_dim)

        # Calculate the total number of inputs after flattening the observation space
        num_inputs = observation_space.shape[0] * observation_space.shape[1]
        
        
        # Define the custom architecture
        self.network = nn.Sequential(
            nn.Flatten(),  # Flatten the observation [23, 5] -> [115]
            nn.Linear(num_inputs, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, features_dim),  # Output layer for 23 binary actions
            nn.Sigmoid()  # Use sigmoid to map the output to [0, 1] for each action
        )

    def forward(self, observations):
        # No need to print the shape here, unless for debugging
        # print('observation shape ',observations.shape)
        return self.network(observations)


class PPOAgent:
    def __init__(self, env):
        self.model = PPO("MlpPolicy", 
                         env, 
                         policy_kwargs={
                                        "features_extractor_class": CustomNetwork ,
                                        "features_extractor_kwargs": {"features_dim": env.action_space.shape[0]}                                       
                                        },
                         verbose=1)
        

    def train(self, total_timesteps):
        self.model.learn(total_timesteps=total_timesteps)

    def save(self, path):
        self.model.save(path)


class Trainer:
    def __init__(self, env, total_timesteps=10000):
        self.env =env
        self.agent = PPOAgent(self.env)
        self.total_timesteps = total_timesteps

    def train_model(self):
        self.agent.train(self.total_timesteps)

    def save_model(self, path):
        self.agent.save(path)


# The CustomNetwork class defines a multi-layer neural network. 
# This can be adjusted based on the complexity of your environment.
        
# The PPOAgent class initializes the PPO model with the custom network.
        
# The Trainer class simplifies the training process. It creates the environment, 
# initializes the agent, runs the training, and saves the model.
        
# We have to Ensure the PaintShopEnv is registered as a Gym environment and is compatible with the Stable Baselines framework.
# We may need to fine-tune the architecture of the CustomNetwork and other hyperparameters based on the specifics of your environment and training performance.
