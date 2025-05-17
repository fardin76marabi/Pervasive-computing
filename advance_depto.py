import math
import random
import matplotlib.pyplot as plt
import numpy as np



numOfFogDevices=10
numOfCloudServers=2
numOfTasks=10    ## it is 100 
numOfGateways=3
numOfIotDevices=20

densityOfInput=30
##inputsize=10 to 30 Mb
##outputsize=1 to 30 Mb

gateway_fog_delay=0.005
gateway_cloud_delay=0.3
gateway_iotDevice_delay=0

listOfDeptoLogs=[[],[],[]]
listOfRandomLogs=[[],[],[]]
listOfHCDLogs=[[],[],[]]

recordOfSatisfiedNumber=[]
recordOfSatisfiedDepto=[]       ## For Using MathplotLib
recordOfSatisfiedRandom=[]
recordOfSatisfiedHCD=[]



class Task:
    def __init__(self,id,instruction,ram,deadline,type):
        self.id=id
        self.instruction=instruction
        self.deadline=deadline
        self.ram=ram
        self.doneOnTime=False
        self.offloaded=False
        self.startTime=0
        self.endTime=0
        self.queueTime=0
        # self.downloadTime=0
        self.processTime=0
        # self.uploadTime=0
        # self.satisfied=0
        self.type=type

class ComputingDevice:
    def __init__(self,name,cpu,ram):
        self.name=name
        self.cpu=cpu
        self.ram=ram
        #self.ram=ram
        self.bufferList=[]
    def remained_ram(self):
        total=0
        remain=self.ram
        if len(self.bufferList)==0:
            return remain
        for task in self.bufferList:
            total+=task.ram
        remain= ((self.ram)-total)
        return remain
    def calculate_waiting_time(self):
        total=0
        waiting=0.1
        if len(self.bufferList)==0:
            return total
        for task in self.bufferList:
            total+=task.instruction
        waiting= (total/(self.cpu))
        return waiting

class Gateway:
    def __init__(self,name):
        self.name=name
        self.queue=[[],[],[]]
        self.taskList=[]
        self.listOfConnectedFogs=[]
        self.listOfConnectedIots=[]
        self.offloadingOrderList=[]
    def setTasks(self,tasks):
        self.taskList=tasks
    def taskClassifier(self):
        for task in self.taskList:
            if task.type=="Type1":
                self.queue[0].append(task)
            elif task.type=="Type2":
                self.queue[1].append(task)
            else:
                self.queue[2].append(task) 


def create_device(num,name):
    listOfCom=[]
    cpu=0
    if name=="Fog":
        cpu=random.randint(500, 2000)
        ram=512
    elif name=="Cloud":
        cpu=random.randint(3000, 10000)
        ram=64000
    else:
        cpu=random.randint(200, 800)
        ram=128
    cpu=cpu*(math.pow(10,6))
    for i in range(num):
        listOfCom.append(ComputingDevice(name+str(i),cpu,ram))
    return listOfCom

def create_task(num):
    listOfTask=[]
    arrayOfLength=[random.randint(100, 372),random.randint(1028, 4280),random.randint(5123, 9784)]
    arrayOfDeadline=[round(random.uniform(0.1,0.5), 1),round(random.uniform(0.5,2.5), 1),round(random.uniform(2.5,10), 1)]
    ram=[32,64,128,256]
    randr=random.randint(0, 3)
    for i in range(num):
        rand=random.randint(0, 2)
        listOfTask.append(Task(i,(arrayOfLength[rand]*math.pow(10,6)),ram[randr],arrayOfDeadline[rand],"Type"+str(rand+1)))
    return listOfTask

def create_gateway(num,name):
    listOfGateway=[]
    for i in range(num):
        listOfGateway.append(Gateway(name+str(i)))
    return listOfGateway

def create_gateway_connections(listOfGateways,listOfFogs,listOfIots):
    for i in range (numOfFogDevices):
        (listOfGateways[i%numOfGateways]).listOfConnectedFogs.append(listOfFogs[i])
    for i in range(numOfIotDevices):
        (listOfGateways[i%numOfGateways]).listOfConnectedIots.append(listOfIots[i])


def show_gateway_connections():
    for i in listOfGateways:
        print(i.name+" connected fogs are :")
        for fog in i.listOfConnectedFogs:
            print(fog.name)

def tasks_classifier(listOfGateways,listOfTasks):
    i=0
    bound=int(len(listOfTasks)/numOfGateways)
    for gateway in listOfGateways:
        a=(i*bound)
        b=((i+1)*bound)
        gateway.setTasks(listOfTasks[a:b])
        gateway.taskClassifier()
        i=i+1

def task_offloadingOrder(listOfGateways):
    n1=4    ##time stamp
    n2=9
    for gateway in listOfGateways:
        time=0
        while True:
            if time%n1 ==0:
                if len(gateway.queue[1])>0:
                    gateway.queue[0].append(gateway.queue[1][0])
                    gateway.queue[1].pop(0)
            if time%n2==0:
                if len(gateway.queue[2])>0:
                    gateway.queue[1].append(gateway.queue[2][0])
                    gateway.queue[2].pop(0)
            if  len(gateway.queue[0])>0:
                gateway.offloadingOrderList.append(gateway.queue[0][0])
                gateway.queue[0].pop(0)
            elif len(gateway.queue[1])>0:
                gateway.offloadingOrderList.append(gateway.queue[1][0])
                gateway.queue[1].pop(0)
            elif len(gateway.queue[2])>0:
                gateway.offloadingOrderList.append(gateway.queue[2][0])
                gateway.queue[2].pop(0)
            else:
                break
            time=time+1
            
def Depto(listForDepto):
    for index,gateway in enumerate(listForDepto):
        for device in gateway.listOfConnectedIots+gateway.listOfConnectedFogs+listOfClouds:
            transmitionDelay=0
            if device.name[0]=="F":
                transmitionDelay=gateway_fog_delay
            elif device.name[0]=="C":
                transmitionDelay=gateway_cloud_delay
            else:##device is iot and delay is 0
                transmitionDelay=0           
            for task in gateway.offloadingOrderList:
                waiting_time=device.calculate_waiting_time()
                process_time=task.instruction/device.cpu
                allTime=waiting_time+process_time+transmitionDelay
                if((allTime<=task.deadline) & (device.remained_ram()>=task.ram) & (task.offloaded==False)):
                    device.bufferList.append(task)
                    task.end=allTime
                    task.offloaded=True
                    task.doneOnTime=True
                    report="Task"+str(task.id)+" -> "+task.type+" Go to "+device.name+" ---- "+gateway.name
                    listOfDeptoLogs[index].append(report)
def HCD(listForHCD):
    for index,gateway in enumerate(listForHCD):
        for device in gateway.listOfConnectedIots+gateway.listOfConnectedFogs+listOfClouds:
            transmitionDelay=0
            if device.name[0]=="F":
                transmitionDelay=gateway_fog_delay
            elif device.name[0]=="C":
                transmitionDelay=gateway_cloud_delay
            else:##device is iot and delay is 0
                transmitionDelay=0
            for task in gateway.offloadingOrderList:
                waiting_time=device.calculate_waiting_time()
                process_time=task.instruction/device.cpu
                allTime=waiting_time+process_time+transmitionDelay
                if (task.instruction<=device.cpu) & (task.offloaded==False):
                    device.bufferList.append(task)
                    task.end=allTime
                    task.offloaded=True
                    report="Task"+str(task.id)+" -> "+task.type+" Go to "+device.name+" ---- "+gateway.name
                    listOfHCDLogs[index].append(report) 
                    if allTime<=task.deadline:
                        task.doneOnTime=True

def random_offloading(listForRandom):
    for index,gateway in enumerate(listForRandom):
        #print(gateway.name) 
        for task in gateway.offloadingOrderList:
            #print(task.id)
            randomDevice=random.choice(gateway.listOfConnectedIots+gateway.listOfConnectedFogs+listOfClouds)
            if randomDevice.name[0]=="F":
                transmitionDelay=gateway_fog_delay
            elif randomDevice.name[0]=="C":
                transmitionDelay=gateway_cloud_delay
            else:##device is iot and delay is 0
                transmitionDelay=0
            waiting_time=randomDevice.calculate_waiting_time()
            process_time=task.instruction/randomDevice.cpu
            allTime=waiting_time+process_time+transmitionDelay
            if allTime<=task.deadline:
                 task.doneOnTime=True
            if task.offloaded==False:
                randomDevice.bufferList.append(task)
                task.end=allTime
                #gateway.offloadingOrderList.remove(task)
                task.offloaded=True
                report="Task"+str(task.id)+" -> "+task.type+" Go to "+randomDevice.name+" ---- "+gateway.name
                listOfRandomLogs[index].append(report)

def check_satisfied(inputList):
    total=0
    allTask=0
    for gateway in inputList:
        for task in gateway.offloadingOrderList:
           if task.doneOnTime==True:
            total+=1
           allTask+=1
    if allTask==0:
        return 0
    final=round(((total/allTask)*100),1)
    print("Percent Of satisfied Task are:",final)
    return final


def show_logs(inputLog):
    for gatewayLog in inputLog:
        for rep in gatewayLog:
            print(rep)   

def normalizaion(listOfGateways):
    for gateway in listOfGateways:
        for device in gateway.listOfConnectedIots+gateway.listOfConnectedFogs+listOfClouds:
            device.bufferList.clear()
        for task in gateway.offloadingOrderList:
            task.end=0
            task.offloaded=False
            task.doneOnTime=False
        gateway.taskList=[]## Newly added
        gateway.setTasks([])
        gateway.offloadingOrderList.clear()
        gateway.queue[0].clear()
        gateway.queue[1].clear()
        gateway.queue[2].clear()

def draw_chart():
    # line 1 points
    x1 = np.array(recordOfSatisfiedNumber)
    y1 = np.array(recordOfSatisfiedDepto)
    # plotting the line 1 points
    plt.plot(x1, y1, label = "Depto")

    # line 2 points
    x2 = np.array(recordOfSatisfiedNumber)
    y2 = np.array(recordOfSatisfiedRandom)
    # plotting the line 2 points
    plt.plot(x2, y2, label = "Random")

    # line 3 points
    x3 = np.array(recordOfSatisfiedNumber)
    y3 = np.array(recordOfSatisfiedHCD)
    # plotting the line 3 points
    plt.plot(x3, y3, label = "HCD")

    # naming the x axis
    plt.xlabel('Number Of Tasks')
    # naming the y axis
    plt.ylabel('Percent Of Satisfiction')
    # giving a title to my graph
    plt.title('Average Number Of Tasks Meeting Deadlines.')

    # show a legend on the plot
    plt.legend()

    # function to show the plot
    plt.show()



listOfFogs=create_device(numOfFogDevices,"Fog")
listOfGateways=create_gateway(numOfGateways,"Gateway")
listOfClouds=create_device(numOfCloudServers,"Cloud")
listOfIotDevices=create_device(numOfIotDevices,"Iot")
#listOfTasks=create_task(numOfTasks)



create_gateway_connections(listOfGateways,listOfFogs,listOfIotDevices)

# listForDepto=listOfGateways.copy()
# listForRandom=listOfGateways.copy()

#show_gateway_connections()




i=0;
number=100
listOfTasksAll=create_task(number)
iteration=10
length=number/iteration

while (i<iteration):
    a=0
    b=int((i+1)*length)
    number=b-a
    listOfTasks=listOfTasksAll[a:b]
    recordOfSatisfiedNumber.append(number)
    print("N = ",number)
    # tasks_classifier(listOfGateways,listOfTasks)
    # task_offloadingOrder(listOfGateways)
    #
    normalizaion(listOfGateways)
    print("#########################################################")
    print("Depto")
    tasks_classifier(listOfGateways,listOfTasks)
    task_offloadingOrder(listOfGateways)
    Depto(listOfGateways)
    sat=check_satisfied(listOfGateways)
    #show_logs(listOfDeptoLogs)
    recordOfSatisfiedDepto.append(sat)
    #
    normalizaion(listOfGateways)
    print("#########################################################")
    print("Random")
    tasks_classifier(listOfGateways,listOfTasks)
    task_offloadingOrder(listOfGateways)
    random_offloading(listOfGateways)
    sat=check_satisfied(listOfGateways)
    #show_logs(listOfRandomLogs)
    recordOfSatisfiedRandom.append(sat)
    #
    normalizaion(listOfGateways)
    print("#########################################################")
    print("HCD")
    tasks_classifier(listOfGateways,listOfTasks)
    task_offloadingOrder(listOfGateways)
    HCD(listOfGateways)
    sat=check_satisfied(listOfGateways)
    #show_logs(listOfHCDLogs)
    recordOfSatisfiedHCD.append(sat)
    print("\n")
    #
    i+=1


draw_chart()