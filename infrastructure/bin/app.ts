#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { NetworkStack } from '../lib/stacks/network-stack';
import { StorageStack } from '../lib/stacks/storage-stack';
import { ComputeStack } from '../lib/stacks/compute-stack';

const app = new cdk.App();

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
};

// Network Stack
const networkStack = new NetworkStack(app, 'ClipMindNetworkStack', { env });

// Storage Stack
const storageStack = new StorageStack(app, 'ClipMindStorageStack', {
  env,
  vpc: networkStack.vpc,
});

// Compute Stack
const computeStack = new ComputeStack(app, 'ClipMindComputeStack', {
  env,
  vpc: networkStack.vpc,
  database: storageStack.database,
});

app.synth();
