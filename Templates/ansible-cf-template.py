"""Generating CloudFormation template.""" 
from ipaddress import ip_network
 
from ipify import get_ip
from troposphere import ( 
    Base64, 
    ec2, 
    GetAtt, 
    Join, 
    Output, 
    Parameter, 
    Ref, 
    Template, 
) 
ApplicationName = "helloworld"
ApplicationPort = "3000" 
PublicCidrIp = str(ip_network(get_ip()))

GithubAccount = "gane-dev"
GithubAnsibleURL = "https://github.com/{}/ansible".format(GithubAccount)
t = Template() 
AnsiblePullCmd =  "/usr/local/bin/ansible-pull -U {} {}.yml -i localhost".format( 
        GithubAnsibleURL, 
        ApplicationName 
    ) 


t.add_description("Simple HelloWorld web application") 

t.add_parameter(Parameter( 
    "GaneshAwsDevOps2", 
    Description="GaneshAwsDevOps2", 
    Type="AWS::EC2::KeyPair::KeyName", 
    ConstraintDescription="must be the name of an existing EC2 KeyPair.", 
)) 

t.add_resource(ec2.SecurityGroup( 
    "SecurityGroup", 
    GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort), 
    SecurityGroupIngress=[ 
        ec2.SecurityGroupRule( 
            IpProtocol="tcp", 
            FromPort="22", 
            ToPort="22", 
            CidrIp=PublicCidrIp, 
        ), 
        ec2.SecurityGroupRule( 
            IpProtocol="tcp", 
            FromPort=ApplicationPort, 
            ToPort=ApplicationPort, 
            CidrIp=PublicCidrIp, 
        ), 
    ], 
)) 

ud = Base64(Join('\n', [
    "#!/bin/bash",
    "yum install --enablerepo=epel -y git",
    "pip install ansible",
    AnsiblePullCmd,
    "echo '*/10 * * * * {}' > /etc/cron.d/ansible-pull".format(AnsiblePullCmd)
]))

t.add_resource(ec2.Instance( 
    "templatedInstanceGaneshAws", 
    ImageId="ami-1853ac65", 
    InstanceType="t2.micro", 
    SecurityGroups=[Ref("SecurityGroup")], 
    KeyName=Ref("GaneshAwsDevOps2"), 
    UserData=ud, 
))  

t.add_output(Output( 
    "InstancePublicIp", 
    Description="Public IP of our instance.", 
    Value=GetAtt("templatedInstanceGaneshAws", "PublicIp"), 
)) 
 
t.add_output(Output( 
    "WebUrl", 
    Description="Application endpoint", 
    Value=Join("", [ 
        "http://", GetAtt("templatedInstanceGaneshAws", "PublicDnsName"), 
        ":", ApplicationPort
    ]), 
)) 

print (t.to_json())