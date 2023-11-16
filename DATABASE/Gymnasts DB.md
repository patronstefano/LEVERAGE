---
database-plugin: basic
FX_Final_Score: NaN
PH_Final_Score: NaN
SR_Final_Score: NaN
VT_Final_Score: NaN
HB_Final_Score: NaN
AA_Final_Score: NaN
PB_Final_Score: NaN
AA_D_Score: NaN
---

```yaml:dbfolder
name: Gymnasts DB
description: Database of Gymnasts
columns:
  Surname:
    input: text
    accessorKey: Surname
    label: Surname
    key: Surname
    id: Surname
    position: 2
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 66
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  Name:
    input: text
    accessorKey: Name
    label: Name
    key: Name
    id: Name
    position: 3
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 72
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  Country:
    input: select
    accessorKey: Country
    label: Country
    key: Country
    id: Country
    position: 5
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 70
    options:
      - { label: "Italy", value: "Italy", color: "hsl(212,100%,72%)"}
      - { label: "Germany", value: "Germany", color: "hsl(0,100%,78%)"}
      - { label: "France", value: "France", color: "hsl(110,100%,75%)"}
      - { label: "Spain", value: "Spain", color: "hsl(55,100%,80%)"}
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
      option_source: manual
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
    width: 69
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: true
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      footer_formula: 
      wrap_content: true
  Category:
    input: select
    accessorKey: Category
    key: Category
    id: Category
    label: Category
    position: 6
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 80
    options:
      - { label: "Junior", value: "Junior", color: "hsl(211,100%,79%)"}
      - { label: "Senior", value: "Senior", color: "hsl(0,100%,79%)"}
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
  Exercises:
    input: relation
    accessorKey: Exercises
    key: Exercises
    id: Exercises
    label: Exercises
    position: 10
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 178
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: true
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      related_note_path: DATABASE/Exercises DB.md
      relation_color: hsl(0,0%,47%)
      bidirectional_relation: true
  Target_Elements:
    input: relation
    accessorKey: Target_Elements
    key: Target_Elements
    id: Target_Elements
    label: Target Elements
    position: 12
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 311
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: true
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      related_note_path: MAG CODE OF POINTS/MAG CODE OF POINTS DB.md
      wrap_content: false
      relation_color: hsl(0,100%,74%)
  Championship:
    input: rollup
    accessorKey: Championship
    key: Championship
    id: Championship
    label: Championships
    position: 8
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 12
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: Gymnasts
      rollup_action: Original Value
      rollup_key: Championship
      wrap_content: false
  Vaults:
    input: relation
    accessorKey: Vaults
    key: Vaults
    id: Vaults
    label: Vaults
    position: 11
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 344
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: true
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      related_note_path: MAG CODE OF POINTS/MAG CODE OF POINTS DB.md
      relation_color: hsl(214,100%,75%)
  Results:
    input: relation
    accessorKey: Results
    key: Results
    id: Results
    label: Results
    position: 9
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 264
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: true
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      related_note_path: DATABASE/Results DB.md
      bidirectional_relation: true
      relation_color: hsl(170,100%,33%)
      wrap_content: false
  Gymnasts:
    input: relation
    accessorKey: Gymnasts
    key: Gymnasts
    id: Gymnasts
    label: Teams
    position: 7
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 327
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: true
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      relation_color: hsl(273,100%,30%)
      related_note_path: DATABASE/Teams DB.md
      bidirectional_relation: true
  Date_of_Birth:
    input: calendar
    accessorKey: Date_of_Birth
    label: Date of Birth
    key: Date_of_Birth
    id: Year_of_birth
    position: 4
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 95
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
  source_form_result: "#GYMNAST"
  source_destination_path: MY DATA/My Gymnasts
  row_templates_folder: /TEMPLATES
  current_row_template: DATABASE/TEMPLATES/New Gymnast.md
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