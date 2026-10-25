# Notion: the project, its tasks and its documentation

The owner (2026-10-19) asked for the project to be kept up to date in their Notion while we work:
"the code base, documentations, researches, tasks, PR". This note is how: where each thing goes, how the
databases relate, what to update at each step of a phase, and the page of every file and phase already
there. The repository stays the source of truth; Notion mirrors it, summarised and linked.

Claude updates Notion through the Notion connector (the `mcp__Notion__*` tools) during the session. Nothing
in the repository calls Notion, and no token is kept anywhere.

## Where each thing goes

| What | Notion | Its page or data source |
|---|---|---|
| The project | **World BIM Platform**, a Project in G/P/R DB | page `3f0cbfcc3a388044a55ffa8af0adead8` (data source `collection://0cee9d47-b3fa-4db1-8e28-3bf844b860c1`) |
| Phases (tasks) | Internal Task DB | `collection://116a8dcf-c55a-4117-9314-f2d817793fb5` |
| Research notes, the plan, PIPELINE, the build contract, the log, the guide | Documentation DB | `collection://ed82f30c-ef60-43e9-8e4f-2d90d87a8942` |
| Pull requests | a line in the phase's task page, under Pull requests | (no database of their own) |

## The relations (two-way; set one side and Notion fills the other)

- Documentation DB **Projects** <-> G/P/R DB **Related Documentations**. Every doc of this project has Projects = World BIM Platform.
- Internal Task DB **Related G/P/R** <-> G/P/R DB **Tasks**. Every phase has Related G/P/R = World BIM Platform.
- Internal Task DB **Documentation** <-> Documentation DB **Related Tasks**. A phase lists the notes it was researched or built from.

Checked 2026-10-19: a doc created with Projects set appeared in the project's Related Documentations.

## The fields we fill

**A phase** (Internal Task DB): Task Name `V### Title` (as PIPELINE's ordered path names it); Type `Deliverables`
(`Work Package` for a track or the V1-V138 history); Status `Inbox` (planned), `In Progress` (being researched or built,
or its PR is open), `Completed` (its PR merged), `Paused` (parked); Task Overview, the scope in a sentence or a few;
Completed on (hide), the merge date; Related G/P/R; Documentation. The page: Scope, Notes, Pull requests.

**A document** (Documentation DB): Name, the file's own title; Record Type `Report` (a research note, the log),
`Specification` (the plan, PIPELINE), `SOP` (the build contract, CLAUDE.md, the research protocol), `Manual` (the user
guide), `Reference` (third-party notices); Description; URL, the file on GitHub's main branch; Version, the phases it
serves; Status `Active`; Authors/ Creators `Brad Pham, with Claude Code`; Projects. The page: the source link, a summary,
the file's sections, and the line that GitHub is the source of truth. Never the file's full text.

## At each step of a phase

1. **Research starts:** the phase's task to `In Progress`. A new research note gets a Documentation DB page (Projects, and
   the phase in its Related Tasks); an amended note gets its page's Contents and Description brought up to date.
2. **The owner's decisions:** they are in the note; its page's summary says they were asked and what was chosen.
3. **PR opened:** a line under the task's Pull requests, `(open)`.
4. **PR merged:** the line says `(merged YYYY-MM-DD)`; the task to `Completed` with Completed on; its scope as built;
   the next phase in PIPELINE marked Start here goes to `In Progress` when its work begins.
5. **The project page:** its "Where the project stands" table (build, hash, size, tests, Now, Next) from PIPELINE.md.
6. **A new phase or row in PIPELINE's ordered path:** a new task; a row removed or renumbered: its task renamed or
   archived, never left stale. Add the new page to the tables below in the same commit.

Search Notion before creating anything, so nothing is made twice.

## Documentation DB pages

| File | Page |
|---|---|
| `CLAUDE.md` | `3fecbfcc3a3881398724f1ee2fd9765e` |
| `CLAUDE_INSTRUCTIONS.md` | `3fecbfcc3a3881448252ca6f0316e029` |
| `PIPELINE.md` | `3fecbfcc3a38814686afe3fbf3c64882` |
| `THIRD_PARTY_NOTICES.md` | `3fecbfcc3a3881518161cc8c65e511c6` |
| `canvas_v10_STATUS.md` | `3fecbfcc3a388169bcdcfb4f0ab28149` |
| `docs/src/` | `3fecbfcc3a38817784eccd9b91488ee9` |
| `reference/plan-v167-v170.md` | `3fecbfcc3a3881de90ecc1541d3685ea` |
| `reference/research-access-people.md` | `3fecbfcc3a3881598684fed1479bb711` |
| `reference/research-analysis-workspace.md` | `404cbfcc3a3881aaa157c4d99f450c3d` |
| `reference/research-alignment.md` | `3fecbfcc3a3881e881cdd2408e75b9a5` |
| `reference/research-animation.md` | `403cbfcc3a388101837ec19cf0e0a894` |
| `reference/research-traffic.md` | `403cbfcc3a388128b93be79356396b92` |
| `reference/research-arcgis-site-analysis.md` | `3fecbfcc3a388106bad2c9be7ba8111c` |
| `reference/research-archidiagram.md` | `3fecbfcc3a388195adb9e5492391d6e2` |
| `reference/research-assets.md` | `3fecbfcc3a38811a8256d14749e71ebd` |
| `reference/research-bim-hub.md` | `3fecbfcc3a3881bea10cea15da11cf25` |
| `reference/research-bridge-splatting.md` | `3fecbfcc3a3881498a60ca0023b27baf` |
| `reference/research-climate-risk-presentation.md` | `3fecbfcc3a388187a1d4ecefbe1cae25` |
| `reference/research-colour-by.md` | `3fecbfcc3a3881d8bf07c622edde1065` |
| `reference/research-command-ui.md` | `3fecbfcc3a388116877ad4d6ba1f045d` |
| `reference/research-data-layers.md` | `3fecbfcc3a38813daa7afbbaf0e0d980` |
| `reference/research-direct-manipulation.md` | `3fecbfcc3a3881eb8b12d278112ac615` |
| `reference/research-field-autonomy.md` | `3fecbfcc3a38819990fed43c7289488e` |
| `reference/research-giraffe.md` | `3fecbfcc3a3881e5a131fafce16dcc73` |
| `reference/research-lod-reconstruction.md` | `3fecbfcc3a38812abfbcd3f4172e02bd` |
| `reference/research-map.md` | `3fecbfcc3a3881b3a039fa3dba8ea81b` |
| `reference/research-mep-runs.md` | `3fecbfcc3a3881708aacf7e7009c4487` |
| `reference/research-one-analyze-boards.md` | `3fecbfcc3a3881efaae7f1be56cb24da` |
| `reference/research-open-data-portals.md` | `3fecbfcc3a388185b82cd124ddf0113c` |
| `reference/research-open-data.md` | `3fecbfcc3a3881a3a64ee704bbaa49b0` |
| `reference/research-panels.md` | `3fecbfcc3a3881908e46fb3e820de67a` |
| `reference/research-presentation-panels.md` | `3fecbfcc3a388173b1cfc01bc48185ab` |
| `reference/research-protocol.md` | `3fecbfcc3a38816aa733fe59b1b78c06` |
| `reference/research-rhino-guide-gap.md` | `3fecbfcc3a38817bb142c5ac90f40b59` |
| `reference/research-scale.md` | `3fecbfcc3a38810a913afad3f717a22f` |
| `reference/research-shortcuts-ui.md` | `3fecbfcc3a38817da2f7e01e671abde6` |
| `reference/research-site-analysis-in-model.md` | `3fecbfcc3a388110af17e44a1e218379` |
| `reference/research-site-analysis-process.md` | `3fecbfcc3a388173ac14ca668847413c` |
| `reference/research-site-context.md` | `3fecbfcc3a3881d694bac9967c6cd6a7` |
| `reference/research-sketchup-import.md` | `3fecbfcc3a3881be999bf09d57837e20` |
| `reference/research-standards-inventory.md` | `3fecbfcc3a3881acab9be7601d152b90` |
| `reference/research-standards-registry.md` | `3fecbfcc3a38810cab96f27728e46d6e` |
| `reference/research-structural-ui.md` | `3fecbfcc3a38818d8c70d61677ab9d5e` |
| `reference/research-survey-check.md` | `3fecbfcc3a3881628cfcc1c30a343b34` |
| `reference/research-tools-panel.md` | `3fecbfcc3a3881a48a6ce529e29f7876` |
| `reference/research-usages.md` | `3fecbfcc3a3881ac8050e475f67cc902` |
| `reference/research-valdrada.md` | `3fecbfcc3a3881b1a8b7edb323f75420` |
| `reference/research-zoning-envelope-yield.md` | `3fecbfcc3a388107b391f35fd6a8f7d4` |

## Internal Task DB pages

| Phase | Page |
|---|---|
| V1-V138 The foundation (history) | `3fecbfcc3a38811091eee95d34c77629` |
| V139 | `3fecbfcc3a388191a761f899ca4bb879` |
| V140 | `3fecbfcc3a388116bac4f0e21719b4a3` |
| V141 | `3fecbfcc3a388133ba2ad5bf240b9216` |
| V142 | `3fecbfcc3a3881e384adfe918bf18266` |
| V143 | `3fecbfcc3a38815692b3e520b0d9edca` |
| V144 | `3fecbfcc3a38818ca12dc5d962b4a82b` |
| V145 | `3fecbfcc3a3881f4a0fcd8f7eb7c66f0` |
| V146 | `3fecbfcc3a3881ba97cff98677d2ccee` |
| V147 | `3fecbfcc3a38811083adfb73fc9f8e4c` |
| V148 | `3fecbfcc3a388122bb52cf96d662edc9` |
| V149 | `3fecbfcc3a3881628863c7ce21213f27` |
| V150 | `3fecbfcc3a3881d48fece8d183665f60` |
| V151 | `3fecbfcc3a3881758b7aca180b21b86a` |
| V152 | `3fecbfcc3a3881c2971dc7e69f9b8697` |
| V153 | `3fecbfcc3a38815699b6c3521cfca138` |
| V154 | `3fecbfcc3a38811d8e17e88a8c99c36b` |
| V155 | `3fecbfcc3a3881d597d6e300170b4254` |
| V156 | `3fecbfcc3a3881168419daea89f50a05` |
| V157 | `3fecbfcc3a38814883eaef2dd4b7ed27` |
| V158 | `3fecbfcc3a3881e882a7fa1434175475` |
| V159 | `3fecbfcc3a3881c19a1ff01c6785b4ed` |
| V160 | `3fecbfcc3a38811b8251c9ccfd9a501c` |
| V161 | `3fecbfcc3a3881c2adabf36ab6278f08` |
| V162 | `3fecbfcc3a3881c3964ce78e839d7b59` |
| V163 | `3fecbfcc3a3881e79559db154dfced5e` |
| V164 | `3fecbfcc3a3881d0b846f07a4ff6f2e3` |
| V165 | `3fecbfcc3a388186a9b1e5a6eccdca6e` |
| V166 | `3fecbfcc3a388191a1fcc176d00b209e` |
| V166b | `3fecbfcc3a3881f19de6f77eb7f8d347` |
| V166c | `3fecbfcc3a3881f4bec7cb7bbd9cbf5c` |
| V166d | `3fecbfcc3a38812bb2bfe7f2e0631161` |
| V167 | `3fecbfcc3a388132921aee72ead0c1cf` |
| V168 | `3fecbfcc3a38819ea14fec6546a55a73` |
| V169 | `3fecbfcc3a38813098bfc7c8d9a46ab0` |
| V170 | `3fecbfcc3a3881aeb276e581b5d92a82` |
| V171 | `3fecbfcc3a388111b74dd9bad2a315d9` |
| V171b | `404cbfcc3a388112900bf36f1efc99d9` |
| V172 | `3fecbfcc3a3881f799a3d2f2e1114a23` |
| V173 | `3fecbfcc3a388141a93be73520d09591` |
| V174 | `3fecbfcc3a3881fa9594ef43af9d6616` |
| V175 | `3fecbfcc3a3881488c3ae42826615c67` |
| V176 | `3fecbfcc3a38811e932ed521acc186e9` |
| V177-V180 | `3fecbfcc3a388109b937fdf301083454` |
| V181-V187 | `3fecbfcc3a38811e8e25f016056867ea` |
| V188 | `3fecbfcc3a38812691a7f52601578c42` |
| V189 | `3fecbfcc3a3881baa390c40baabde95e` |
| V190 | `3fecbfcc3a38810ab991c79844dc90a6` |
| V191 | `3fecbfcc3a38810dbe2ef80dc00f4720` |
| V192 | `3fecbfcc3a3881129f8ae5f8b618ce71` |
| V193 | `3fecbfcc3a3881829582fb0df50b56d1` |
| Source split: the app in src/, by feature (PR #49) | `404cbfcc3a38811dbbc9d382d02a9c81` |
| Later: Model import (glTF, valdrada's models) | `3fecbfcc3a3881a8aac2ccef7bcee713` |
| Later: Hub H3, full IFC | `3fecbfcc3a3881f38adaf9da8b70bf26` |
| Later: Hub H4, share and sync | `3fecbfcc3a3881a0ae89deed1c5dab5c` |
| Later: Hub H5, the server | `3fecbfcc3a3881139bc7ed9832d6b76a` |
| Later: Streaming | `3fecbfcc3a3881e3a2c7f3e240ba7f89` |
| Later: Rendering on WebGPU | `3fecbfcc3a388102af55eae8049f4eb6` |
| Later: Water and presentation rendering | `3fecbfcc3a38819a8f57e83effb3d081` |
| Later: Structural and wind analysis | `3fecbfcc3a388188b060ced595518127` |
| Later: Survey control | `3fecbfcc3a3881c3ade9ffb1b87d3e18` |
| Later: Generators | `3fecbfcc3a38811ca674e1ee19166f0a` |
| Later: Costs and pro forma | `3fecbfcc3a388174af7aed4154fd905a` |
| Later: Flows and an app SDK | `3fecbfcc3a38812e97e1d103cae7d4cd` |
| Later: Track E, field work and autonomy | `3fecbfcc3a3881898c8cee95145f1705` |
| Parked: Tracks C and D (bridges) | `3fecbfcc3a3881c6aed2e8c24cb225f7` |

## Found while mirroring (2026-10-19)

- PIPELINE's "later" row **Rendering on WebGPU** still says "the renderer is our own WebGL today", written before V152 to
  V156 built the WebGPU engine. What is left of it is compute shaders for the simulations; its task says so.
- PIPELINE's "later" row **Structural and wind analysis** asks for a frame solver, which V125 built (Frame analysis).
  What is left is wind by lattice Boltzmann; its task says so.
- The old Notion page **CAD/ BIM** (Tools / Application DB) describes the build of 2026-09-09 (Phase 55). It was left
  as it is; World BIM Platform is the project now.
- 2026-10-19: Archi Diagram's animated analysis became a new V170 (the owner); the phases from the old V170 on moved
  one number later, their tasks renamed and the table above with them.
