---

database-plugin: basic

---

```yaml:dbfolder
name: Results DB
description: Database of Results
columns:
  __file__:
    key: __file__
    id: __file__
    input: markdown
    label: File
    accessorKey: __file__
    isMetadata: true
    skipPersist: false
    isDragDisabled: false
    csvCandidate: true
    position: 1
    isHidden: false
    sortIndex: -1
    width: 114
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: true
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      wrap_content: true
  Results:
    input: relation
    accessorKey: Results
    key: Results
    id: Results
    label: Gymnast
    position: 4
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 156
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: true
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      related_note_path: DATABASE/Gymnasts DB.md
      bidirectional_relation: true
      relation_color: hsl(0,0%,0%)
  Teams:
    input: rollup
    accessorKey: Teams
    key: Teams
    id: Teams
    label: Team
    position: 5
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 218
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: true
      task_hide_completed: true
      footer_type: none
      persist_changes: true
      asociated_relation_id: Results
      rollup_action: Original Value
      rollup_key: Gymnasts
      wrap_content: true
  FX_D_Score:
    input: number
    accessorKey: FX_D_Score
    key: FX_D_Score
    id: FX_D_Score
    label: FX D Score
    position: 6
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 14
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      footer_formula: 
  FX_E_Score:
    input: number
    accessorKey: FX_E_Score
    key: FX_E_Score
    id: FX_E_Score
    label: FX E Score
    position: 7
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 11
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      footer_formula: 
  FX_Final_Score:
    input: formula
    accessorKey: FX_Final_Score
    key: FX_Final_Score
    id: FX_Score
    label: FX Final Score
    position: 9
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 31
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: true
      formula_query: ${row.FX_D_Score+row.FX_E_Score-row.FX_ND}
  PH_D_Score:
    input: number
    accessorKey: PH_D_Score
    key: PH_D_Score
    id: PH_D_Score
    label: PH D Score
    position: 10
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 10
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  PH_E_Score:
    input: number
    accessorKey: PH_E_Score
    key: PH_E_Score
    id: PH_E_Score
    label: PH E Score
    position: 11
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 6
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  PH_Final_Score:
    input: formula
    accessorKey: PH_Final_Score
    key: PH_Final_Score
    id: PH_Final_Score
    label: PH Final Score
    position: 13
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 44
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: true
      formula_query: ${row.PH_D_Score+row.PH_E_Score-row.PH_ND}
  SR_D_Score:
    input: number
    accessorKey: SR_D_Score
    key: SR_D_Score
    id: SR_D_Score
    label: SR D Score
    position: 14
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 1
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  SR_E_Score:
    input: number
    accessorKey: SR_E_Score
    key: SR_E_Score
    id: SR_E_Score
    label: SR E Score
    position: 15
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 23
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  SR_Final_Score:
    input: formula
    accessorKey: SR_Final_Score
    key: SR_Final_Score
    id: SR_Final_Score
    label: SR Final Score
    position: 17
    skipPersist: false
    isHidden: false
    sortIndex: -1
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: true
      formula_query: ${row.SR_D_Score+row.SR_E_Score-row.SR_ND}
  VT_D_Score:
    input: number
    accessorKey: VT_D_Score
    key: VT_D_Score
    id: VT_D_Score
    label: VT D Score
    position: 18
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 53
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  VT_E_Score:
    input: number
    accessorKey: VT_E_Score
    key: VT_E_Score
    id: VT_E_Score
    label: VT E Score
    position: 19
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 19
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  VT_Final_Score:
    input: formula
    accessorKey: VT_Final_Score
    key: VT_Final_Score
    id: VT_Final_Score
    label: VT Final Score
    position: 21
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: -12
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: true
      formula_query: ${row.VT_D_Score+row.VT_E_Score-row.VT_ND}
  PB_D_Score:
    input: number
    accessorKey: PB_D_Score
    key: PB_D_Score
    id: PB_D_Score
    label: PB D Score
    position: 22
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 14
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  PB_E_Score:
    input: number
    accessorKey: PB_E_Score
    key: PB_E_Score
    id: PB_E_Score
    label: PB E Score
    position: 23
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: -2
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  PB_Final_Score:
    input: formula
    accessorKey: PB_Final_Score
    key: PB_Final_Score
    id: PB_Final_Score
    label: PB Final Score
    position: 25
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 28
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: true
      formula_query: ${row.PB_D_Score+row.PB_E_Score-row.PB_ND}
  HB_D_Score:
    input: number
    accessorKey: HB_D_Score
    key: HB_D_Score
    id: HB_D_Score
    label: HB D Score
    position: 26
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 3
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  HB_E_Score:
    input: number
    accessorKey: HB_E_Score
    key: HB_E_Score
    id: HB_E_Score
    label: HB E Score
    position: 27
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: -4
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  HB_Final_Score:
    input: formula
    accessorKey: HB_Final_Score
    key: HB_Final_Score
    id: HB_Final_Score
    label: HB Final Score
    position: 29
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 25
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: true
      formula_query: ${row.HB_D_Score+row.HB_E_Score-row.HB_ND}
  AA_D_Score:
    input: formula
    accessorKey: AA_D_Score
    key: AA_D_Score
    id: AA_D_Score
    label: AA D Score
    position: 30
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 194
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: true
      formula_query: ${row.FX_D_Score+row.PH_D_Score+row.SR_D_Score+row.VT_D_Score+row.PB_D_Score+row.HB_D_Score+60}
  AA_Final_Score:
    input: formula
    accessorKey: AA_Final_Score
    key: AA_Final_Score
    id: AA_Final_Score
    label: AA Final Score
    position: 31
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 115
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: true
      formula_query: ${row.FX_D_Score+row.PH_D_Score+row.SR_D_Score+row.VT_D_Score+row.PB_D_Score+row.HB_D_Score+row.FX_E_Score+row.PH_E_Score+row.SR_E_Score+row.VT_E_Score+row.PB_E_Score+row.HB_E_Score-row.FX_ND+row.PH_ND+row.SR_ND+row.VT_ND+row.PB_ND+row.HB_ND}
  Competition:
    input: select
    accessorKey: Competition
    key: Competition
    id: Competition
    label: Competition
    position: 2
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 90
    options:
      - { label: "Serie A1", value: "Serie A1", color: "hsl(238,100%,57%)"}
      - { label: "Serie A2", value: "Serie A2", color: "hsl(225,100%,76%)"}
      - { label: "Serie B", value: "Serie B", color: "hsl(200,100%,68%)"}
      - { label: "Serie C", value: "Serie C", color: "hsl(201,100%,85%)"}
      - { label: "Top 12", value: "Top 12", color: "hsl(130,100%,59%)"}
      - { label: "1.Bundesliga", value: "1.Bundesliga", color: "hsl(0,100%,59%)"}
      - { label: "2.Bundesliga", value: "2.Bundesliga", color: "hsl(41,100%,59%)"}
      - { label: "3.Bundesliga", value: "3.Bundesliga", color: "hsl(64,100%,58%)"}
      - { label: "Assoluti", value: "Assoluti", color: "hsl(305,100%,69%)"}
      - { label: "Categoria", value: "Categoria", color: "hsl(281,100%,62%)"}
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      option_source: manual
  Date_of_Competition:
    input: calendar
    accessorKey: Date_of_Competition
    key: Date_of_Competition
    id: Date_of_Competition
    label: Date of Competition
    position: 3
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 100
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  FX_ND:
    input: number
    accessorKey: FX_ND
    key: FX_ND
    id: FX_Penalities
    label: FX ND
    position: 8
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 10
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      footer_formula: 
  PH_ND:
    input: number
    accessorKey: PH_ND
    key: PH_ND
    id: PH_Penalities
    label: PH ND
    position: 12
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: -48
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  SR_ND:
    input: number
    accessorKey: SR_ND
    key: SR_ND
    id: SR_Penalities
    label: SR ND
    position: 16
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 52
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  VT_ND:
    input: number
    accessorKey: VT_ND
    key: VT_ND
    id: VT_Penalities
    label: VT ND
    position: 20
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 43
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  PB_ND:
    input: number
    accessorKey: PB_ND
    key: PB_ND
    id: PB_Penalities
    label: PB ND
    position: 24
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 22
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  HB_ND:
    input: number
    accessorKey: HB_ND
    key: HB_ND
    id: HB_Penalities
    label: HB ND
    position: 28
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 47
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
config:
  remove_field_when_delete_column: false
  cell_size: normal
  sticky_first_column: true
  group_folder_column: 
  remove_empty_folders: false
  automatically_group_files: false
  hoist_files_with_empty_attributes: false
  show_metadata_created: false
  show_metadata_modified: false
  show_metadata_tasks: false
  show_metadata_inlinks: false
  show_metadata_outlinks: false
  source_data: tag
  source_form_result: "#RESULT"
  source_destination_path: MY DATA/My Results
  row_templates_folder: /
  current_row_template: DATABASE/TEMPLATES/New Result.md
  pagination_size: 200
  font_size: 16
  enable_js_formulas: false
  formula_folder_path: /
  inline_default: false
  inline_new_position: last_field
  date_format: yyyy-MM-dd
  datetime_format: "yyyy-MM-dd HH:mm:ss"
  metadata_date_format: "yyyy-MM-dd HH:mm:ss"
  enable_footer: false
  implementation: default
filters:
  enabled: false
  conditions:
```