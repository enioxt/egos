import type { EgosModule } from '@egos/core/module';

export class ModuleRegistry {
  private readonly modules = new Map<string, EgosModule>();

  register(module: EgosModule): void {
    if (this.modules.has(module.manifest.id)) {
      throw new Error(`Module already registered: ${module.manifest.id}`);
    }

    this.modules.set(module.manifest.id, module);
  }

  get(moduleId: string): EgosModule | undefined {
    return this.modules.get(moduleId);
  }

  list(): EgosModule[] {
    return [...this.modules.values()];
  }
}
