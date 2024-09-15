# app/services/etdqn.py
import numpy as np
import torch as th
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

# Hyperparameters
LEARNING_RATE = 0.001
GAMMA = 0.99  # Discount factor for future rewards
MEMORY_SIZE = 10000
BATCH_SIZE = 64

device = th.device("cuda" if th.cuda.is_available() else "cpu")  # Define the device

class ETDQN:
    def __init__(self, input_dim, output_dim, lr=0.005, gamma=0.9, epsilon=0.9, epsilon_decay=None):
        self.eval_net = DuelingNet(input_dim, output_dim, [128, 64], activation_fn=nn.ReLU)
        self.target_net = DuelingNet(input_dim, output_dim, [128, 64], activation_fn=nn.ReLU)

        self.eval_net.to(device)
        self.target_net.to(device)
        
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay

        self.optimizer = th.optim.Adam(self.eval_net.parameters(), lr)
        self.loss_fn = nn.SmoothL1Loss()
        self.memory = []
        self.batch_size = 32

    def store_transition(self, s, a, r, s_, done):
        transition = (s, a, r, s_, done)
        self.memory.append(transition)
        if len(self.memory) > 2000:  # Maintain memory size
            self.memory.pop(0)

    def choose_action(self, state):
        if np.random.uniform() < self.epsilon:
            action = np.random.choice([0, 1])  # Explore randomly (0: Skip, 1: Download)
        else:
            state = th.FloatTensor(state).unsqueeze(0).to(device)
            actions_value = self.eval_net(state)
            action = th.argmax(actions_value).item()  # Choose action with the highest Q-value
        return action

    def learn(self):
        if len(self.memory) < self.batch_size:
            return
        
        # Sample batch
        transitions = np.random.choice(self.memory, self.batch_size)
        batch = np.array(transitions)
        
        states = np.vstack(batch[:, 0])
        actions = th.LongTensor(batch[:, 1].tolist()).unsqueeze(1).to(device)
        rewards = th.FloatTensor(batch[:, 2].tolist()).unsqueeze(1).to(device)
        next_states = np.vstack(batch[:, 3])
        dones = th.FloatTensor(batch[:, 4].tolist()).unsqueeze(1).to(device)

        q_eval = self.eval_net(th.FloatTensor(states).to(device)).gather(1, actions)
        q_next = self.target_net(th.FloatTensor(next_states).to(device)).detach().max(1)[0].unsqueeze(1)

        q_target = rewards + (self.gamma * q_next * (1 - dones))
        loss = self.loss_fn(q_eval, q_target)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update epsilon
        if self.epsilon_decay:
            self.epsilon = max(0.1, self.epsilon - self.epsilon_decay)

        # Target network update
        self.target_net.load_state_dict(self.eval_net.state_dict())
