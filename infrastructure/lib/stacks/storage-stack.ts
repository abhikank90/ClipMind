import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

export interface StorageStackProps extends cdk.StackProps {
  vpc: ec2.Vpc;
}

export class StorageStack extends cdk.Stack {
  public readonly database: rds.DatabaseInstance;
  public readonly videosBucket: s3.Bucket;

  constructor(scope: Construct, id: string, props: StorageStackProps) {
    super(scope, id, props);

    // S3 Bucket for videos
    this.videosBucket = new s3.Bucket(this, 'VideosBucket', {
      versioned: false,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // PostgreSQL Database
    this.database = new rds.DatabaseInstance(this, 'Database', {
      engine: rds.DatabaseInstanceEngine.postgres({
        version: rds.PostgresEngineVersion.VER_15_3,
      }),
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.T3,
        ec2.InstanceSize.MEDIUM
      ),
      vpc: props.vpc,
      allocatedStorage: 100,
      databaseName: 'clipmind',
      removalPolicy: cdk.RemovalPolicy.SNAPSHOT,
    });
  }
}
