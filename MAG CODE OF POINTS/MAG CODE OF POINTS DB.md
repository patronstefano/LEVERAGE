---

database-plugin: basic

---

```yaml:dbfolder
name: MAG CODE OF POINTS DB
description: Database of Men's Artistic Gymnastics Code of Points 2022-2024
columns:
  Alias:
    input: text
    accessorKey: Alias
    label: Name
    key: Alias
    id: Alias
    position: 2
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 103
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      wrap_content: true
      content_alignment: text-align-center
      content_vertical_alignment: align-middle
  Image:
    input: relation
    accessorKey: Image
    label: Image
    key: Image
    id: Image
    position: 3
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 294
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      relation_color: hsl(0,0%,100%)
      content_alignment: text-align-center
      content_vertical_alignment: align-middle
  Symbol:
    input: relation
    accessorKey: Symbol
    label: Symbol
    key: Symbol
    id: Symbol
    position: 4
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 142
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      relation_color: hsl(0,0%,100%)
      content_alignment: text-align-center
      content_vertical_alignment: align-middle
  Code:
    input: number
    accessorKey: Code
    label: Code
    key: Code
    id: Code
    position: 5
    skipPersist: false
    isHidden: false
    sortIndex: 3
    width: 24
    isSorted: true
    isSortedDesc: false
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: false
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      content_alignment: text-align-center
      content_vertical_alignment: align-middle
  Apparatus:
    input: select
    accessorKey: Apparatus
    label: Apparatus
    key: Apparatus
    id: Apparatus
    position: 6
    skipPersist: false
    isHidden: false
    sortIndex: 1
    isSorted: true
    isSortedDesc: false
    width: 52
    options:
      - { label: "FX", value: "FX", color: "hsl(0,100%,50%)"}
      - { label: "PH", value: "PH", color: "hsl(58,100%,50%)"}
      - { label: "SR", value: "SR", color: "hsl(121,100%,50%)"}
      - { label: "VT", value: "VT", color: "hsl(184,100%,50%)"}
      - { label: "PB", value: "PB", color: "hsl(299,100%,50%)"}
      - { label: "HB", value: "HB", color: "hsl(225,100%,50%)"}
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
  EG:
    input: select
    accessorKey: EG
    label: EG
    key: EG
    id: EG
    position: 7
    skipPersist: false
    isHidden: false
    sortIndex: 2
    width: 15
    isSorted: true
    isSortedDesc: false
    options:
      - { label: "I", value: "I", color: "hsl(0,0%,100%)"}
      - { label: "II", value: "II", color: "hsl(0,0%,70%)"}
      - { label: "III", value: "III", color: "hsl(0,0%,36%)"}
      - { label: "IV", value: "IV", color: "hsl(0,0%,0%)"}
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
    width: 328
    config:
      enable_media_view: true
      link_alias_enabled: true
      media_width: 100
      media_height: 100
      isInline: true
      task_hide_completed: true
      footer_type: none
      persist_changes: false
      content_alignment: text-align-left
      content_vertical_alignment: align-middle
      wrap_content: true
  DV:
    input: select
    accessorKey: DV
    label: DV
    key: DV
    id: Value
    position: 8
    skipPersist: false
    isHidden: false
    sortIndex: -1
    width: 21
    options:
      - { label: "A", value: "A", color: "hsl(198,100%,82%)"}
      - { label: "B", value: "B", color: "hsl(233,100%,82%)"}
      - { label: "C", value: "C", color: "hsl(290,100%,82%)"}
      - { label: "D", value: "D", color: "hsl(0,100%,82%)"}
      - { label: "E", value: "E", color: "hsl(32,100%,82%)"}
      - { label: "H", value: "H", color: "hsl(121,100%,83%)"}
      - { label: "F", value: "F", color: "hsl(58,100%,82%)"}
      - { label: "G", value: "G", color: "hsl(90,100%,82%)"}
      - { label: "I", value: "I", color: "hsl(162,100%,82%)"}
      - { label: "5.6", value: "5.6", color: "hsl(191, 95%, 90%)"}
      - { label: "6", value: "6", color: "hsl(172, 95%, 90%)"}
      - { label: "3.6", value: "3.6", color: "hsl(314, 95%, 90%)"}
      - { label: "4", value: "4", color: "hsl(184, 95%, 90%)"}
      - { label: "4.4", value: "4.4", color: "hsl(331, 95%, 90%)"}
      - { label: "4.8", value: "4.8", color: "hsl(276, 95%, 90%)"}
      - { label: "5.2", value: "5.2", color: "hsl(6, 95%, 90%)"}
      - { label: "3.2", value: "3.2", color: "hsl(122, 95%, 90%)"}
      - { label: "2", value: "2", color: "hsl(223, 95%, 90%)"}
      - { label: "2.2", value: "2.2", color: "hsl(135, 95%, 90%)"}
      - { label: "1.8", value: "1.8", color: "hsl(108, 95%, 90%)"}
      - { label: "2.4", value: "2.4", color: "hsl(161, 95%, 90%)"}
      - { label: "2.6", value: "2.6", color: "hsl(330, 95%, 90%)"}
      - { label: "1.6", value: "1.6", color: "hsl(271, 95%, 90%)"}
      - { label: "2.8", value: "2.8", color: "hsl(147, 95%, 90%)"}
      - { label: "5.4", value: "5.4", color: "hsl(153, 95%, 90%)"}
      - { label: "3", value: "3", color: "hsl(150, 95%, 90%)"}
      - { label: "3.4", value: "3.4", color: "hsl(271, 95%, 90%)"}
      - { label: "4.6", value: "4.6", color: "hsl(322, 95%, 90%)"}
      - { label: "4.2", value: "4.2", color: "hsl(268, 95%, 90%)"}
      - { label: "5.8", value: "5.8", color: "hsl(139, 95%, 90%)"}
      - { label: "3.8", value: "3.8", color: "hsl(343, 95%, 90%)"}
      - { label: "5", value: "5", color: "hsl(228, 95%, 90%)"}
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
  Type:
    input: tags
    accessorKey: Type
    key: Type
    id: Type
    label: Type
    position: 9
    skipPersist: false
    isHidden: true
    sortIndex: -1
    width: 291
    options:
      - { label: "PH_Handstand_element", value: "PH_Handstand_element", color: "hsl(94, 95%, 90%)"}
      - { label: "PH_Combined_element_without_russian", value: "PH_Combined_element_without_russian", color: "hsl(194, 95%, 90%)"}
      - { label: "PH_Combined_element_with_russian", value: "PH_Combined_element_with_russian", color: "hsl(85, 95%, 90%)"}
      - { label: "FX_Strength_element", value: "FX_Strength_element", color: "hsl(147, 95%, 90%)"}
      - { label: "FX_Circle_element", value: "FX_Circle_element", color: "hsl(222, 95%, 90%)"}
      - { label: "FX_Single_salto_element_without_turns", value: "FX_Single_salto_element_without_turns", color: "hsl(66, 95%, 90%)"}
      - { label: "FX_Multiple_salto_element", value: "FX_Multiple_salto_element", color: "hsl(185, 95%, 90%)"}
      - { label: "FX_Fwd_landing_element", value: "FX_Fwd_landing_element", color: "hsl(76, 95%, 90%)"}
      - { label: "FX_Bwd_landing_element", value: "FX_Bwd_landing_element", color: "hsl(287, 95%, 90%)"}
      - { label: "PH_Russian_element", value: "PH_Russian_element", color: "hsl(63, 95%, 90%)"}
      - { label: "PH_On_the_end_element", value: "PH_On_the_end_element", color: "hsl(15, 95%, 90%)"}
      - { label: "PH_Between_pommels_element", value: "PH_Between_pommels_element", color: "hsl(72, 95%, 90%)"}
      - { label: "PH_Russian_travel_element", value: "PH_Russian_travel_element", color: "hsl(69, 95%, 90%)"}
      - { label: "PH_Cross_support_travel_element", value: "PH_Cross_support_travel_element", color: "hsl(241, 95%, 90%)"}
      - { label: "PH_Spindle_element", value: "PH_Spindle_element", color: "hsl(334, 95%, 90%)"}
      - { label: "PH_Spindle_travel_element", value: "PH_Spindle_travel_element", color: "hsl(108, 95%, 90%)"}
      - { label: "PH_Sohn_element", value: "PH_Sohn_element", color: "hsl(153, 95%, 90%)"}
      - { label: "PH_Bezugo_element", value: "PH_Bezugo_element", color: "hsl(96, 95%, 90%)"}
      - { label: "SR_Swing_to_handstand_element", value: "SR_Swing_to_handstand_element", color: "hsl(43, 95%, 90%)"}
      - { label: "SR_Swing_element", value: "SR_Swing_element", color: "hsl(49, 95%, 90%)"}
      - { label: "SR_Guczoghy_element", value: "SR_Guczoghy_element", color: "hsl(74, 95%, 90%)"}
      - { label: "SR_Cross_element", value: "SR_Cross_element", color: "hsl(29, 95%, 90%)"}
      - { label: "SR_Inverted_cross_element", value: "SR_Inverted_cross_element", color: "hsl(284, 95%, 90%)"}
      - { label: "SR_Support_scale_element", value: "SR_Support_scale_element", color: "hsl(173, 95%, 90%)"}
      - { label: "SR_Swallow_element", value: "SR_Swallow_element", color: "hsl(99, 95%, 90%)"}
      - { label: "SR_Inverted_swallow_element", value: "SR_Inverted_swallow_element", color: "hsl(19, 95%, 90%)"}
      - { label: "SR_L_sit_element", value: "SR_L_sit_element", color: "hsl(131, 95%, 90%)"}
      - { label: "SR_V_sit_element", value: "SR_V_sit_element", color: "hsl(54, 95%, 90%)"}
      - { label: "SR_Hanging_scale_element", value: "SR_Hanging_scale_element", color: "hsl(92, 95%, 90%)"}
      - { label: "PB_One_bar_element", value: "PB_One_bar_element", color: "hsl(214, 95%, 90%)"}
      - { label: "PB_Upgraded_element", value: "PB_Upgraded_element", color: "hsl(338, 95%, 90%)"}
      - { label: "PB_Morisue_element", value: "PB_Morisue_element", color: "hsl(208, 95%, 90%)"}
      - { label: "PB_Salto_fwd_straddled_element", value: "PB_Salto_fwd_straddled_element", color: "hsl(307, 95%, 90%)"}
      - { label: "PB_Double_salto_fwd_element", value: "PB_Double_salto_fwd_element", color: "hsl(323, 95%, 90%)"}
      - { label: "PB_Salto_fwd_element", value: "PB_Salto_fwd_element", color: "hsl(175, 95%, 90%)"}
      - { label: "PB_Dimitrenko_element", value: "PB_Dimitrenko_element", color: "hsl(109, 95%, 90%)"}
      - { label: "PB_Pakhniuk_element", value: "PB_Pakhniuk_element", color: "hsl(275, 95%, 90%)"}
      - { label: "PB_Harada_element", value: "PB_Harada_element", color: "hsl(39, 95%, 90%)"}
      - { label: "PB_Belle_element", value: "PB_Belle_element", color: "hsl(253, 95%, 90%)"}
      - { label: "PB_Tanaka_element", value: "PB_Tanaka_element", color: "hsl(227, 95%, 90%)"}
      - { label: "PB_Torres_element", value: "PB_Torres_element", color: "hsl(43, 95%, 90%)"}
      - { label: "PB_Gagnon_element", value: "PB_Gagnon_element", color: "hsl(22, 95%, 90%)"}
      - { label: "PB_Tejada_element", value: "PB_Tejada_element", color: "hsl(248, 95%, 90%)"}
      - { label: "PB_Giant_swing_element", value: "PB_Giant_swing_element", color: "hsl(212, 95%, 90%)"}
      - { label: "PB_Basket_swing_element", value: "PB_Basket_swing_element", color: "hsl(15, 95%, 90%)"}
      - { label: "HB_Adler_element", value: "HB_Adler_element", color: "hsl(156, 95%, 90%)"}
      - { label: "HB_Rybalko_element", value: "HB_Rybalko_element", color: "hsl(110, 95%, 90%)"}
      - { label: "HB_Swing_with_turn_element", value: "HB_Swing_with_turn_element", color: "hsl(74, 95%, 90%)"}
      - { label: "HB_Stalder_rybalko_element", value: "HB_Stalder_rybalko_element", color: "hsl(311, 95%, 90%)"}
      - { label: "HB_Adler_with_turn_element", value: "HB_Adler_with_turn_element", color: "hsl(143, 95%, 90%)"}
      - { label: "HB_Quintero_element", value: "HB_Quintero_element", color: "hsl(220, 95%, 90%)"}
      - { label: "HB_Tkatchev_piatti_element", value: "HB_Tkatchev_piatti_element", color: "hsl(257, 95%, 90%)"}
      - { label: "HB_Kovacs_element", value: "HB_Kovacs_element", color: "hsl(121, 95%, 90%)"}
      - { label: "PROHIBITED_FOR_JUNIOR", value: "PROHIBITED_FOR_JUNIOR", color: "hsl(0,0%,0%)"}
      - { label: "ADDITIONAL_ELEMENT", value: "ADDITIONAL_ELEMENT", color: "hsl(0,0%,100%)"}
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
  source_data: query
  source_form_result: "FROM \"MAG CODE OF POINTS\" WHERE Code!=NULL"
  source_destination_path: /
  row_templates_folder: /
  current_row_template: 
  pagination_size: 200
  font_size: 15
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
  enabled: true
  conditions:
      - condition: AND
        disabled: true
        label: "FX"
        color: "hsl(0,100%,50%)"
        filters:
        - field: Apparatus
          operator: EQUAL
          value: "FX"
      - condition: AND
        disabled: true
        label: "PH"
        color: "hsl(61,100%,50%)"
        filters:
        - field: Apparatus
          operator: EQUAL
          value: "PH"
      - condition: AND
        disabled: true
        label: "SR"
        color: "hsl(119,100%,50%)"
        filters:
        - field: Apparatus
          operator: EQUAL
          value: "SR"
      - condition: AND
        disabled: true
        label: "VT"
        color: "hsl(187,100%,50%)"
        filters:
        - field: Apparatus
          operator: EQUAL
          value: "VT"
      - condition: AND
        disabled: true
        label: "PB"
        color: "hsl(305,100%,50%)"
        filters:
        - field: Apparatus
          operator: EQUAL
          value: "PB"
      - condition: AND
        disabled: true
        label: "HB"
        color: "hsl(230,100%,50%)"
        filters:
        - field: Apparatus
          operator: EQUAL
          value: "HB"
      - condition: AND
        disabled: true
        label: "EG I"
        color: "hsl(0,0%,100%)"
        filters:
        - field: EG
          operator: EQUAL
          value: "I"
      - condition: AND
        disabled: true
        label: "EG II"
        color: "hsl(0,0%,76%)"
        filters:
        - field: EG
          operator: EQUAL
          value: "II"
      - condition: AND
        disabled: true
        label: "EG III"
        color: "hsl(0,0%,40%)"
        filters:
        - field: EG
          operator: EQUAL
          value: "III"
      - condition: AND
        disabled: true
        label: "EG IV"
        color: "hsl(0,0%,0%)"
        filters:
        - field: EG
          operator: EQUAL
          value: "IV"
      - condition: AND
        disabled: true
        label: "PROHIBITED FOR JUNIOR"
        color: "hsl(0,100%,81%)"
        filters:
        - field: Type
          operator: CONTAINS
          value: "PROHIBITED_FOR_JUNIOR"
      - condition: AND
        disabled: true
        label: "ADDITIONAL ELEMENTS"
        color: "hsl(209,100%,83%)"
        filters:
        - field: Type
          operator: CONTAINS
          value: "ADDITIONAL_ELEMENT"
```