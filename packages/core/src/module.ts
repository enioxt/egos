export interface EgosModuleManifest {
  id: string;
  name: string;
  version: string;
  description: string;
  provides: string[];
  dependsOn: string[];
  entrypoint: string;
  configSchemaRef?: string;
  permissions?: string[];
  tags?: string[];
}

export interface EgosModule {
  manifest: EgosModuleManifest;
  setup(): Promise<void>;
  start?(): Promise<void>;
  stop?(): Promise<void>;
}
