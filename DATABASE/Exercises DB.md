---

database-plugin: basic

---

```yaml:dbfolder
name: Exercises DB
description: Database of Exercises
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
  Apparatus:
    input: select
    accessorKey: Apparatus
    key: Apparatus
    id: Apparatus
    label: Apparatus
    position: 5
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 90
    options:
      - { label: "FX", value: "FX", color: "hsl(0,100%,50%)"}
      - { label: "PH", value: "PH", color: "hsl(61,100%,50%)"}
      - { label: "SR", value: "SR", color: "hsl(132,100%,50%)"}
      - { label: "PB", value: "PB", color: "hsl(296,100%,50%)"}
      - { label: "HB", value: "HB", color: "hsl(244,100%,50%)"}
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
  1_DV:
    input: rollup
    accessorKey: 1_DV
    key: 1_DV
    id: 1_DV
    label: DV
    position: 9
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 42
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: 1_Element
      rollup_action: Original Value
      rollup_key: DV
  1_EG:
    input: rollup
    accessorKey: 1_EG
    key: 1_EG
    id: 1_EG
    label: EG
    position: 10
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 2
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: 1_Element
      rollup_action: Original Value
      rollup_key: EG
  1+2:
    input: checkbox
    accessorKey: 1+2
    key: 1+2
    id: 1+2
    label: 1+2
    position: 11
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 9
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  2_Element:
    input: relation
    accessorKey: 2_Element
    key: 2_Element
    id: 2_Element
    label: 2 Element
    position: 12
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 392
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
      relation_color: hsl(0,0%,50%)
  2_DV:
    input: rollup
    accessorKey: 2_DV
    key: 2_DV
    id: 2_DV
    label: DV
    position: 13
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 33
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: 2_Element
      rollup_action: Original Value
      rollup_key: DV
  2_EG:
    input: rollup
    accessorKey: 2_EG
    key: 2_EG
    id: 2_EG
    label: EG
    position: 14
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
      asociated_relation_id: 2_Element
      rollup_action: Original Value
      rollup_key: EG
  2+3:
    input: checkbox
    accessorKey: 2+3
    key: 2+3
    id: 2+3
    label: 2+3
    position: 15
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: -8
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  3_Element:
    input: relation
    accessorKey: 3_Element
    key: 3_Element
    id: 3_Element
    label: 3 Element
    position: 16
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 370
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
      relation_color: hsl(0,0%,50%)
  3_DV:
    input: rollup
    accessorKey: 3_DV
    key: 3_DV
    id: 3_DV
    label: DV
    position: 17
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
      persist_changes: false
      asociated_relation_id: 3_Element
      rollup_action: Original Value
      rollup_key: DV
  3_EG:
    input: rollup
    accessorKey: 3_EG
    key: 3_EG
    id: 3_EG
    label: EG
    position: 18
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 7
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: 3_Element
      rollup_action: Original Value
      rollup_key: EG
  3+4:
    input: checkbox
    accessorKey: 3+4
    key: 3+4
    id: 3+4
    label: 3+4
    position: 19
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 16
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  4_Element:
    input: relation
    accessorKey: 4_Element
    key: 4_Element
    id: 4_Element
    label: 4 Element
    position: 20
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 393
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
      relation_color: hsl(0,0%,50%)
  4_DV:
    input: rollup
    accessorKey: 4_DV
    key: 4_DV
    id: 4_DV
    label: DV
    position: 21
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
      asociated_relation_id: 4_Element
      rollup_action: Original Value
      rollup_key: DV
  4_EG:
    input: rollup
    accessorKey: 4_EG
    key: 4_EG
    id: 4_EG
    label: EG
    position: 22
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
      asociated_relation_id: 4_Element
      rollup_action: Original Value
      rollup_key: EG
  4+5:
    input: checkbox
    accessorKey: 4+5
    key: 4+5
    id: 4+5
    label: 4+5
    position: 23
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
  5_Element:
    input: relation
    accessorKey: 5_Element
    key: 5_Element
    id: 5_Element
    label: 5 Element
    position: 24
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 369
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
      relation_color: hsl(0,0%,50%)
  5_DV:
    input: rollup
    accessorKey: 5_DV
    key: 5_DV
    id: 5_DV
    label: DV
    position: 25
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: -5
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: 5_Element
      rollup_action: Original Value
      rollup_key: DV
  5_EG:
    input: rollup
    accessorKey: 5_EG
    key: 5_EG
    id: 5_EG
    label: EG
    position: 26
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 2
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: 5_Element
      rollup_action: Original Value
      rollup_key: EG
  5+6:
    input: checkbox
    accessorKey: 5+6
    key: 5+6
    id: 5+6
    label: 5+6
    position: 27
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: -1
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  6_Element:
    input: relation
    accessorKey: 6_Element
    key: 6_Element
    id: 6_Element
    label: 6 Element
    position: 28
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 391
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
      relation_color: hsl(0,0%,50%)
  6_DV:
    input: rollup
    accessorKey: 6_DV
    key: 6_DV
    id: 6_DV
    label: DV
    position: 29
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: -19
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: 6_Element
      rollup_action: Original Value
      rollup_key: DV
  6_EG:
    input: rollup
    accessorKey: 6_EG
    key: 6_EG
    id: 6_EG
    label: EG
    position: 30
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: -24
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: 6_Element
      rollup_action: Original Value
      rollup_key: EG
  6+7:
    input: checkbox
    accessorKey: 6+7
    key: 6+7
    id: 6+7
    label: 6+7
    position: 31
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 20
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  7_Element:
    input: relation
    accessorKey: 7_Element
    key: 7_Element
    id: 7_Element
    label: 7 Element
    position: 32
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 371
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
      relation_color: hsl(0,0%,50%)
  7_DV:
    input: rollup
    accessorKey: 7_DV
    key: 7_DV
    id: 7_DV
    label: DV
    position: 33
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: -1
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: 7_Element
      rollup_action: Original Value
      rollup_key: DV
  7_EG:
    input: rollup
    accessorKey: 7_EG
    key: 7_EG
    id: 7_EG
    label: EG
    position: 34
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: -15
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: 7_Element
      rollup_action: Original Value
      rollup_key: EG
  7+8:
    input: checkbox
    accessorKey: 7+8
    key: 7+8
    id: 7+8
    label: 7+8
    position: 35
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 48
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  8_Element:
    input: relation
    accessorKey: 8_Element
    key: 8_Element
    id: 8_Element
    label: 8 Element
    position: 36
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 391
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
      relation_color: hsl(0,0%,50%)
  8_DV:
    input: rollup
    accessorKey: 8_DV
    key: 8_DV
    id: 8_DV
    label: DV
    position: 37
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: -1
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: 8_Element
      rollup_action: Original Value
      rollup_key: DV
  8_EG:
    input: rollup
    accessorKey: 8_EG
    key: 8_EG
    id: 8_EG
    label: EG
    position: 38
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 4
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: 8_Element
      rollup_action: Original Value
      rollup_key: EG
  8+9:
    input: checkbox
    accessorKey: 8+9
    key: 8+9
    id: 8+9
    label: 8+9
    position: 39
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 35
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  9_Element:
    input: relation
    accessorKey: 9_Element
    key: 9_Element
    id: 9_Element
    label: 9 Element
    position: 40
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 370
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
      relation_color: hsl(0,0%,50%)
  9_DV:
    input: rollup
    accessorKey: 9_DV
    key: 9_DV
    id: 9_DV
    label: DV
    position: 41
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 29
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: 9_Element
      rollup_action: Original Value
      rollup_key: DV
  9_EG:
    input: rollup
    accessorKey: 9_EG
    key: 9_EG
    id: 9_EG
    label: EG
    position: 42
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
      persist_changes: false
      asociated_relation_id: 9_Element
      rollup_action: Original Value
      rollup_key: EG
  Dismount:
    input: relation
    accessorKey: Dismount
    key: Dismount
    id: Dismount
    label: Dismount
    position: 43
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 430
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
      relation_color: hsl(0,33%,39%)
  D_DV:
    input: rollup
    accessorKey: D_DV
    key: D_DV
    id: D_DV
    label: DV
    position: 44
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
      asociated_relation_id: Dismount
      rollup_action: Original Value
      rollup_key: DV
  D_EG:
    input: rollup
    accessorKey: D_EG
    key: D_EG
    id: D_EG
    label: EG
    position: 45
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 0
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      asociated_relation_id: Dismount
      rollup_action: Original Value
      rollup_key: EG
  1_Element:
    input: relation
    accessorKey: 1_Element
    key: 1_Element
    id: 1_Element
    label: 1 Element
    position: 8
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 371
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
      relation_color: hsl(0,0%,50%)
  Exercises:
    input: relation
    accessorKey: Exercises
    key: Exercises
    id: Exercises
    label: Gymnast
    position: 2
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 138
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
      relation_color: hsl(0,0%,0%)
      bidirectional_relation: true
  Category:
    input: rollup
    accessorKey: Category
    key: Category
    id: Category
    label: Category
    position: 3
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 78
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: true
      asociated_relation_id: Exercises
      rollup_action: Original Value
      rollup_key: Category
  Target_Date:
    input: calendar
    accessorKey: Target_Date
    key: Target_Date
    id: Target_Date
    label: Target Date
    position: 4
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 90
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
  CV:
    input: number
    accessorKey: CV
    key: CV
    id: CV
    label: CV
    position: 7
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
  D_Score:
    input: number
    accessorKey: D_Score
    key: D_Score
    id: D_Score
    label: D Score
    position: 6
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
  source_form_result: "#EXERCISE"
  source_destination_path: MY DATA/My Exercises
  row_templates_folder: /
  current_row_template: DATABASE/TEMPLATES/New Exercise.md
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