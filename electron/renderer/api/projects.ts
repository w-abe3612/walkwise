/**
 * electron/renderer/api/projects.ts — 公開契約: listProjects/createProject.
 *
 * Contract: docs/test-cases/TASK-UI-001-project-list-and-create-screen.md
 * Spec: docs/screens/01-project-list-and-create.md
 */

export interface ProjectSummaryDto {
  readonly projectId: string;
  readonly title: string;
  readonly planningStage: string;
  readonly updatedAt: string;
}

export interface CreateProjectFormInput {
  readonly title: string;
  readonly domain: string;
  readonly purpose: string;
  readonly usagePurpose: string;
  readonly targetAudienceDescription: string;
  readonly sourceStrategy: readonly string[];
}

export interface ListProjectsResult {
  readonly projects: readonly ProjectSummaryDto[];
}

export interface WalkwiseProjectApi {
  list(): Promise<ListProjectsResult>;
  create(input: CreateProjectFormInput): Promise<ProjectSummaryDto>;
}

function resolveDefaultApi(): WalkwiseProjectApi {
  const walkwise = (globalThis as unknown as { walkwise?: { project?: WalkwiseProjectApi } }).walkwise;
  if (!walkwise?.project) {
    throw new Error("window.walkwise.project API is not available");
  }
  return walkwise.project;
}

/** preload APIを型付きで呼ぶ(既定はrendererへ公開済みの`window.walkwise.project`)。 */
export async function listProjects(api: WalkwiseProjectApi = resolveDefaultApi()): Promise<ListProjectsResult> {
  return api.list();
}

export async function createProject(
  input: CreateProjectFormInput,
  api: WalkwiseProjectApi = resolveDefaultApi(),
): Promise<ProjectSummaryDto> {
  return api.create(input);
}
