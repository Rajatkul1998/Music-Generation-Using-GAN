from Dataset import Dataset
import CONFIG
from Generator import Generator
from Discriminator import Discriminator
import pickle
import numpy as np
import Data_functions
import torch
import torch.nn as nn
import torch.optim as optim

with open('./Intermediate Files/Converted_notes_to_int.bin','rb') as f1:
    main_list = pickle.load(f1)

data=Dataset(main_list,CONFIG.batch_size)

tensor_data=data.convert_to_tensor()

dataloader=data.dataloader(tensor_data)

gen = Generator(CONFIG.input_size,CONFIG.hidden_size,CONFIG.gen_output_size,CONFIG.n_layers)

dis = Discriminator(CONFIG.gen_output_size,CONFIG.hidden_size,CONFIG.dis_output_size,CONFIG.n_layers)

criteriond1 = nn.BCELoss()
optimizerd1 = optim.Adam(dis.parameters(), lr=0.001)

criteriond2 = nn.BCELoss()
optimizerd2 = optim.Adam(gen.parameters(), lr=0.001)

epochs = CONFIG.epochs

epoch_dis_loss=[]
epoch_gen_loss=[]
for epoch in range(epochs):
  dis.train()
  gen.train()  
  h_dis = dis.init_hidden(CONFIG.batch_size)
  h_gen= gen.init_hidden(CONFIG.batch_size)

  generator_loss=[]
  discriminator_loss=[]
  for vec in dataloader:
    h_discriminator = tuple([e.data for e in h_dis])  
    h_generator=  tuple([e.data for e in h_gen])
    #Training of Discriminator
    dis.zero_grad()
    vec=torch.tensor(vec).to(torch.int64)
    dis_real_out,h_discriminator=dis(vec,h_discriminator)
    dis_real_loss=criteriond1(dis_real_out,Data_functions.real_data_target(vec.size(0)))

    inp_fake_x_gen1=Data_functions.make_some_noise(vec.size(0))
    inp_fake_x_gen1=torch.tensor(inp_fake_x_gen1).to(torch.int64)
    
    #print(inp_fake_x_gen1)

    dis_inp_fake_x,h_generator=gen(inp_fake_x_gen1,h_generator)
    dis_inp_fake_x=torch.tensor(dis_inp_fake_x).to(torch.int64)
    dis_fake_out,h_discriminator=dis(dis_inp_fake_x.detach(),h_discriminator)
    dis_fake_loss=criteriond1(dis_fake_out,Data_functions.fake_data_target(vec.size(0)))

    lossD=dis_real_loss+dis_fake_loss
    discriminator_loss.append(lossD.item())
    lossD.backward()
    
    optimizerd1.step()

    #Training of Generator
    
    gen.zero_grad()
    gen_out,h_generator=gen(inp_fake_x_gen1,h_generator)
    gen_out=torch.tensor(gen_out).to(torch.int64)
    dis_out ,h_discriminator= dis(gen_out,h_discriminator)
    gen_loss = criteriond2(dis_out,Data_functions.real_data_target(vec.size(0)))
    generator_loss.append(gen_loss.item())
    gen_loss.backward()
     
    optimizerd2.step()
  epoch_dis_loss.append(np.mean(discriminator_loss))
  epoch_gen_loss.append(np.mean(generator_loss))
  print("Epoch:{}".format(epoch),"    Discriminator loss:{}".format(np.mean(discriminator_loss)),"    Generator  loss:{}".format(np.mean(generator_loss))) 


torch.save(gen.state_dict(), './Intermediate Files/model.pth')

