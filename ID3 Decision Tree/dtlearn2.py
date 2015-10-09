'''
Created on 24-Sep-2015

@author: satyamdhar
'''
import sys
import arff
import math


trainingData = arff.load(open(sys.argv[1], 'rb'))
m=int(sys.argv[2])
testData = arff.load(open('/Users/satyamdhar/Desktop/diabetes_test.arff.txt', 'rb'))
targetIndex=len(trainingData['data'][0])-1
class treeNode :
    def __init__(self,label):
        self.label=label
        self.index=-1
        self.positives=[]
        self.negatives=[]
        self.attributeType='none'
        self.children=[]
        self.values=[]
        self.threshold=0
    def addChildNode(self,label):
        self.children.append(label)

class trainInst :
    def __init__(self, instance):
        self.attrValues=instance
        
    def setAttrVal(self,AttributeIndex):
        self.value=self.attrValues[AttributeIndex]
    
    def display(self):
        print self.attrValues

class nominalAttribute :
    def __init__(self,attribute,nominalAttributeIndex):
        self.name=attribute[0]
        self.values=attribute[1]
        self.index=nominalAttributeIndex

class numericAttribute :
    def __init__(self,attribute,numericAttributeIndex):
        self.name=attribute[0]
        self.index=numericAttributeIndex

def compareSets(set1, set2):
    for instance1 in set1 :
        for instance2 in set2 :
            if instance1.attrValues[targetIndex]!=instance2.attrValues[targetIndex] :
                return False
    return True

def determineCandidateNumericSplits(setInstances,numericAttributeIndex):
    candidateSplits=[];
    for objInstance in setInstances:
        objInstance.setAttrVal(numericAttributeIndex)
    
    setInstances.sort(key=lambda x: x.value)
    valuesOfAttr=[]
    for instance in setInstances:
        if(valuesOfAttr.__contains__(instance.value)==False):
            valuesOfAttr.append(instance.value)
    S=[]
    for value in valuesOfAttr:
        s=[]
        for instance in setInstances:
            if instance.value==value :
                s.append(instance)
        S.append(s)
    if len(S)==1:
        candidateSplits.append(value)
    else :
        for i in range(0,len(S)-1) :
            if(compareSets(S[i],S[i+1])==False) :
                candidateSplits.append((valuesOfAttr[i]+valuesOfAttr[i+1])/2.0)
    return candidateSplits

def findBestSplitEntropy(setInstances, numericAttributeIndex, candidateSplits):
    entropyOfCandidateSplits=[]
    for val in candidateSplits:
        gPositives=0
        gNegatives=0
        sPositives=0
        sNegatives=0
        for instance in setInstances:
            if(instance.attrValues[numericAttributeIndex]<=val):
                if instance.attrValues[targetIndex]=='positive':
                    gPositives+=1
                else :
                    gNegatives+=1
            else:
                if instance.attrValues[targetIndex]=='positive':
                    sPositives+=1
                else :
                    sNegatives+=1
        eSmaller=((sPositives+sNegatives)/(float(len(setInstances))))*entropy(sPositives, sNegatives)
        eGreater=((gPositives+gNegatives)/(float(len(setInstances))))*entropy(gPositives,gNegatives)
        entropyOfCandidateSplits.append(eGreater+eSmaller)
    if not entropyOfCandidateSplits:
        return (0,-1)
    else:
        return (min(entropyOfCandidateSplits),entropyOfCandidateSplits.index(min(entropyOfCandidateSplits)))

def findEntropyNominal(setInstances, attribute):
    entropyOfAttrVal=[]
    for aValue in attribute.values:
        positives=0
        negatives=0
        for instance in setInstances:
            if(instance.attrValues[attribute.index]==aValue):
                if instance.attrValues[targetIndex]=='positive':
                    positives+=1
                else :
                    negatives+=1
        entropyOfAttrVal.append(((positives+negatives)/float(len(setInstances)))*entropy(positives,negatives))
    return sum(entropyOfAttrVal)

def entropy(positives, negatives):
    if(positives!=0 and negatives!=0):
        prob1=positives/float(positives+negatives)
        prob2=negatives/float(positives+negatives)
        return -prob1*math.log(prob1,2)-prob2*math.log(prob2,2)
    else :
        return 0

def findBestAttribute(attributes, setInstances):
    entropyOfAttribute=[]
    for attribute in attributes:
        if isinstance(attribute,nominalAttribute) :
            entropyOfAttribute.append(findEntropyNominal(setInstances,attribute))
        else:
            candidateSplits=determineCandidateNumericSplits(setInstances,attribute.index)
            entropyOfBestSplit,indexOfBestSplit=findBestSplitEntropy(setInstances, attribute.index, candidateSplits)
            entropyOfAttribute.append(entropyOfBestSplit)
    return entropyOfAttribute.index(min(entropyOfAttribute))

def makeSubtree(setInstances, attributes):
    newAttributes=[]
    node=treeNode('empty')
    positives=0
    negatives=0
    for instance in setInstances:
        if instance.attrValues[targetIndex]=='positive':
            positives+=1
        else :
            negatives+=1
#     print 'postives',positives,'negatives',negatives
    if len(setInstances)<m :
        node.attributeType='class'
        if positives > negatives: 
            node.label='positive' 
        else: 
            node.label='negative'
        print ':',node.label,
        return node
    elif(len(setInstances)==positives):
        node.label='positive'
        node.attributeType='class'
        print ':',node.label,
        return node
    elif len(setInstances)==negatives:
        node.label='negative'
        node.attributeType='class'
        print ':',node.label,
        return node
    elif not attributes:
        if positives > negatives: 
            node.label='positive' 
        else: 
            node.label='negative'
        node.attributeType='class'
        print ':',node.label,
        return node
    else:
        bestAttribute=attributes[findBestAttribute(attributes, setInstances)]
        node.label=bestAttribute.name
        node.index=bestAttribute.index
        newSetInstances=[]
        if isinstance(bestAttribute,nominalAttribute):
            node.values=bestAttribute.values
            node.attributeType='nominal'
            for aValue in bestAttribute.values :
                newSetInstances=[]
                
#                 positives=0
#                 negatives=0
                for instance in setInstances:
                    if instance.attrValues[bestAttribute.index]==aValue:
                        newSetInstances.append(instance)
#                 for instance in newSetInstances:
#                     if instance.attrValues[targetIndex]=='positive':
#                         positives+=1
#                     else :
#                         negatives+=1
#                 print positives,negatives
                newAttributes=[]
                for attr in attributes:
                    newAttributes.append(attr)
#                 print len(newAttributes),bestAttribute.index
                newAttributes.pop(bestAttribute.index)
                
                node.children.append(makeSubtree(newSetInstances, newAttributes))
            print '\n',indentStr,node.label," = ",node.values[i],' [',negatives,',',positives,']',
            return node
        else :
            node.attributeType='numeric'
            newSetInstancesGreater=[]
            newSetInstancesSmaller=[]
            candidateSplits=determineCandidateNumericSplits(setInstances, bestAttribute.index)
            entropyOfBestSplit,indexOfBestSplit=findBestSplitEntropy(setInstances, bestAttribute.index, candidateSplits)
            if indexOfBestSplit==-1:
                if positives > negatives: 
                    node.label='positive' 
                else: 
                    node.label='negative'
                node.attributeType='class'
                print ':',node.label,
                return node
            node.threshold=candidateSplits[indexOfBestSplit]
            for instance in setInstances :
                if instance.attrValues[bestAttribute.index]<=candidateSplits[indexOfBestSplit]:
                    newSetInstancesGreater.append(instance)
                    print '\n',indentStr,node.label,"<=",node.threshold,' [',negatives,',',positives,']',
                else :
                    newSetInstancesSmaller.append(instance)
                    print '\n',indentStr,node.label,">",node.threshold,' [',negatives,',',positives,']',
                    
            newAttributes=[]
            for attr in attributes:
                newAttributes.append(attr)
            newAttributes.pop(bestAttribute.index)
            node.children.append(makeSubtree(newSetInstancesGreater, attributes))
            node.children.append(makeSubtree(newSetInstancesSmaller, attributes))
            
            return node
                    
def displayTree(node,indentStr):
    if node.attributeType=='nominal' :
        for i in range(len(node.values)):
            print '\n',indentStr,node.label," = ",node.values[i],#' [',node.negatives[i],',',node.positives[i],']',
            displayTree(node.children[i], indentStr+'|\t')
    elif node.attributeType=='numeric' :
        print '\n',indentStr,node.label,"<=",node.threshold,#' [',node.negatives[0],',',node.positives[0],']',
        displayTree(node.children[0], indentStr+'|\t')
        print '\n',indentStr,node.label,">",node.threshold,#' [',node.negatives[1],',',node.positives[1],']',
        displayTree(node.children[1], indentStr+'|\t')
    elif node.attributeType=='class' :
        print ':',node.label,

def predictClass(node,instance):
    if node.attributeType=='class':
        return node.label
    elif node.attributeType=='nominal' :
        instVal=instance.attrValues[node.index]
        return predictClass(node.children[node.values.index(instVal)], instance)
    elif node.attributeType=='numeric' :
        instVal=instance.attrValues[node.index]
        if instVal <= node.threshold :
            return predictClass(node.children[0], instance)
        else :
            return predictClass(node.children[1], instance)
    else:
        return 'No Class. Your ID3 Algorithm doesn\'t work'
#     if node.attributeType=='nominal':
#         for val in node.values:
#             print node.label,'=',val
#             for child in node.children:
#                 displayTree(child,indent+1)
#     elif node.attributeType=='numeric':
#         print node.label,'<=',node.threshold
#         displayTree(node.children[0],indent+1)
#         print node.label,'>',node.threshold
#         displayTree(node.children[1],indent+1)
#     elif node.attributeType=='class':
#         print node.label

def main():
    trainingInstances=[]    #list of training instance objects
    for instance in trainingData['data']:
        objInstance=trainInst(instance)
        trainingInstances.append(objInstance)
    
    attributes=[]           #list of attribute objects
    for attribute in trainingData['attributes']:
        if isinstance(attribute[1],list):
            nominalAttributeIndex=trainingData['attributes'].index(attribute)
            objAttribute=nominalAttribute(attribute,nominalAttributeIndex)
        else:
            numericAttributeIndex=trainingData['attributes'].index(attribute)
            objAttribute=numericAttribute(attribute,numericAttributeIndex)
        attributes.append(objAttribute)
    attributes.pop(-1)
#     for instance in trainingInstances:
#         print instance.attrValues[targetIndex]
#     print attributes[findBestAttribute(attributes, trainingInstances)].name
#     for attribute in attributes:
#         print attribute.name,attribute.index,isinstance(attribute, nominalAttribute)
    tree=makeSubtree(trainingInstances, attributes)
    displayTree(tree, '')
    print
    print '<Predictions for the Test Set Instances>'
    
    testInstances = []
    for instance in testData['data']:
        objInstance=trainInst(instance)
        testInstances.append(objInstance)
    totalCorrect=0
    for instance in testInstances:
        predictedClass=predictClass(tree,instance)
        print ': Actual:',instance.attrValues[targetIndex],' Predicted: ',predictedClass
        if instance.attrValues[targetIndex]==predictedClass:
            totalCorrect+=1
    print 'Number of correctly classified: ',totalCorrect,'  Total number of test instances: ',len(testInstances)
    
    
    
main()
    #trainingInstances.sort(key=lambda x:x.value)
#     for i in range(len(trainingInstances)):
#         trainingInstances[i].display()
    
         
     
    #print subsetsOfTI
    
#print trainingInstances



# for i in range(len(trainingData['attributes'])):
#         print trainingData['attributes'][i]
#         
# for i in range(len(trainingData['data'][0])):
# #     for j in range(len(trainingData['data'][i])):
#         print trainingData['data'][0][i]
#         
#for i in range(len(trainingData['data'][0])):
     
# def countAttributeProbability(trainingData,i):
#     attrProbTuple=trainingData['attributes'][i][0]
#     sum=0
#     for y in range(trainingData['data'][len(trainingData['data']-1)]):
#         if(y=='positive'):
#             sum=sum+1
#      
#     probability=sum/len(trainingData['data'][i])
#     attrProbTuple.append(probability)
#     return attrProbTuple
# 
# 
# 
# print countAttributeProbability(trainingData, 0)    


