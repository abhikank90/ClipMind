import * as cdk from 'aws-cdk-lib';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

export interface ComputeStackProps extends cdk.StackProps {
  vpc: ec2.Vpc;
  database: any;
}

export class ComputeStack extends cdk.Stack {
  public readonly cluster: ecs.Cluster;

  constructor(scope: Construct, id: string, props: ComputeStackProps) {
    super(scope, id, props);

    this.cluster = new ecs.Cluster(this, 'ClipMindCluster', {
      vpc: props.vpc,
      clusterName: 'clipmind-cluster',
      containerInsights: true,
    });

    new cdk.CfnOutput(this, 'ClusterName', {
      value: this.cluster.clusterName,
    });
  }
}
