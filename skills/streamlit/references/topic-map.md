# Topic Map

Use this map to decide which reference file to load. The list follows the official docs navigation but is reorganized around ChatGPT assistance tasks.

## Official concept links
- Running your app: https://docs.streamlit.io/develop/concepts/architecture/run-your-app
- Streamlit architecture: https://docs.streamlit.io/develop/concepts/architecture/architecture
- Caching concept: https://docs.streamlit.io/develop/concepts/architecture/caching
- Session State concept: https://docs.streamlit.io/develop/concepts/architecture/session-state
- Forms concept: https://docs.streamlit.io/develop/concepts/architecture/forms
- Fragments concept: https://docs.streamlit.io/develop/concepts/architecture/fragments
- Widget behavior: https://docs.streamlit.io/develop/concepts/architecture/widget-behavior
- Multipage apps overview: https://docs.streamlit.io/develop/concepts/multipage-apps/overview
- Page and navigation: https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation
- Pages directory: https://docs.streamlit.io/develop/concepts/multipage-apps/pages-directory
- Layouts and containers: https://docs.streamlit.io/develop/concepts/design/layouts-and-containers
- Buttons concept: https://docs.streamlit.io/develop/concepts/design/buttons
- Dataframes concept: https://docs.streamlit.io/develop/concepts/design/dataframes
- Multithreading: https://docs.streamlit.io/develop/concepts/design/multithreading
- Timezone handling: https://docs.streamlit.io/develop/concepts/design/timezone-handling
- Connecting to data: https://docs.streamlit.io/develop/concepts/connections/connecting-to-data
- Secrets management: https://docs.streamlit.io/develop/concepts/connections/secrets-management
- User authentication: https://docs.streamlit.io/develop/concepts/connections/authentication
- Security reminders: https://docs.streamlit.io/develop/concepts/connections/security-reminders
- App testing: https://docs.streamlit.io/develop/concepts/app-testing
- Configuration options: https://docs.streamlit.io/develop/concepts/configuration/options
- Theming: https://docs.streamlit.io/develop/concepts/configuration/theming
- Static file serving: https://docs.streamlit.io/develop/concepts/configuration/serving-static-files

## Official deployment links
- Community Cloud overview: https://docs.streamlit.io/deploy/streamlit-community-cloud
- Deploy from GitHub: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app
- Manage app dependencies: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies
- Manage secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- Docker deployment concepts: https://docs.streamlit.io/deploy/tutorials/docker
- Kubernetes deployment concepts: https://docs.streamlit.io/deploy/tutorials/kubernetes
- Snowflake deployment: https://docs.streamlit.io/deploy/snowflake

## API command coverage
## Write Magic Text Status

- `st.write` - general-purpose rendering for strings, dataframes, charts, exceptions, and rich objects. Official: https://docs.streamlit.io/develop/api-reference/write-magic/st.write
- `st.write_stream` - streaming tokens or chunks with a typewriter-like user experience. Official: https://docs.streamlit.io/develop/api-reference/write-magic/st.write_stream
- `magic` - automatic rendering of bare expressions when magic is enabled. Official: https://docs.streamlit.io/develop/api-reference/write-magic/magic
- `st.title` - page-level title text. Official: https://docs.streamlit.io/develop/api-reference/text/st.title
- `st.header` - major section headings. Official: https://docs.streamlit.io/develop/api-reference/text/st.header
- `st.subheader` - subsection headings. Official: https://docs.streamlit.io/develop/api-reference/text/st.subheader
- `st.markdown` - markdown content and controlled inline formatting. Official: https://docs.streamlit.io/develop/api-reference/text/st.markdown
- `st.caption` - small explanatory text and footnotes. Official: https://docs.streamlit.io/develop/api-reference/text/st.caption
- `st.badge` - compact status badges. Official: https://docs.streamlit.io/develop/api-reference/text/st.badge
- `st.code` - syntax-highlighted code blocks. Official: https://docs.streamlit.io/develop/api-reference/text/st.code
- `st.echo` - rendering code and its result for tutorials. Official: https://docs.streamlit.io/develop/api-reference/text/st.echo
- `st.latex` - LaTeX math rendering. Official: https://docs.streamlit.io/develop/api-reference/text/st.latex
- `st.text` - preformatted plain text. Official: https://docs.streamlit.io/develop/api-reference/text/st.text
- `st.divider` - visual separation between sections. Official: https://docs.streamlit.io/develop/api-reference/text/st.divider
- `st.html` - isolated HTML snippets when markdown is insufficient. Official: https://docs.streamlit.io/develop/api-reference/text/st.html
- `st.help` - quick inspection of Python objects and functions. Official: https://docs.streamlit.io/develop/api-reference/text/st.help
- `st.success` - positive callouts. Official: https://docs.streamlit.io/develop/api-reference/status/st.success
- `st.info` - neutral informational callouts. Official: https://docs.streamlit.io/develop/api-reference/status/st.info
- `st.warning` - warning callouts. Official: https://docs.streamlit.io/develop/api-reference/status/st.warning
- `st.error` - error callouts. Official: https://docs.streamlit.io/develop/api-reference/status/st.error
- `st.exception` - exception display with tracebacks. Official: https://docs.streamlit.io/develop/api-reference/status/st.exception
- `st.progress` - progress bars for long-running work. Official: https://docs.streamlit.io/develop/api-reference/status/st.progress
- `st.spinner` - temporary loading indicators. Official: https://docs.streamlit.io/develop/api-reference/status/st.spinner
- `st.status` - multi-step status containers. Official: https://docs.streamlit.io/develop/api-reference/status/st.status
- `st.toast` - transient notifications. Official: https://docs.streamlit.io/develop/api-reference/status/st.toast
- `st.balloons` - celebration animation. Official: https://docs.streamlit.io/develop/api-reference/status/st.balloons
- `st.snow` - decorative animation. Official: https://docs.streamlit.io/develop/api-reference/status/st.snow

## Data Charts Media

- `st.dataframe` - interactive dataframe display. Official: https://docs.streamlit.io/develop/api-reference/data/st.dataframe
- `st.data_editor` - editable tabular data with typed columns. Official: https://docs.streamlit.io/develop/api-reference/data/st.data_editor
- `st.column_config` - column type, formatting, validation, and display configuration. Official: https://docs.streamlit.io/develop/api-reference/data/st.column_config
- `st.table` - static table rendering. Official: https://docs.streamlit.io/develop/api-reference/data/st.table
- `st.metric` - KPI and metric display with delta. Official: https://docs.streamlit.io/develop/api-reference/data/st.metric
- `st` JSON display command - expandable JSON inspection. Official: https://docs.streamlit.io/develop/api-reference/data/st JSON display command
- `st.line_chart` - simple line charts. Official: https://docs.streamlit.io/develop/api-reference/charts/st.line_chart
- `st.area_chart` - simple area charts. Official: https://docs.streamlit.io/develop/api-reference/charts/st.area_chart
- `st.bar_chart` - simple bar charts. Official: https://docs.streamlit.io/develop/api-reference/charts/st.bar_chart
- `st.scatter_chart` - simple scatter charts. Official: https://docs.streamlit.io/develop/api-reference/charts/st.scatter_chart
- `st.map` - map visualization from latitude and longitude columns. Official: https://docs.streamlit.io/develop/api-reference/charts/st.map
- `st.altair_chart` - declarative Vega-Lite charts. Official: https://docs.streamlit.io/develop/api-reference/charts/st.altair_chart
- `st.plotly_chart` - interactive Plotly figures. Official: https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart
- `st.pyplot` - Matplotlib figures. Official: https://docs.streamlit.io/develop/api-reference/charts/st.pyplot
- `st.pydeck_chart` - deck.gl map and layer visualizations. Official: https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart
- `st.vega_lite_chart` - Vega-Lite specs. Official: https://docs.streamlit.io/develop/api-reference/charts/st.vega_lite_chart
- `st.graphviz_chart` - Graphviz diagrams. Official: https://docs.streamlit.io/develop/api-reference/charts/st.graphviz_chart
- `st.image` - image display. Official: https://docs.streamlit.io/develop/api-reference/media/st.image
- `st.audio` - audio display. Official: https://docs.streamlit.io/develop/api-reference/media/st.audio
- `st.video` - video display. Official: https://docs.streamlit.io/develop/api-reference/media/st.video
- `st.logo` - app logo branding. Official: https://docs.streamlit.io/develop/api-reference/media/st.logo
- `st.pdf` - PDF display when available. Official: https://docs.streamlit.io/develop/api-reference/media/st.pdf

## Widgets Layout Execution

- `st.button` - momentary actions and explicit user-triggered events. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.button
- `st.download_button` - browser downloads from generated data. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.download_button
- `st.link_button` - buttons that navigate to external links. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.link_button
- `st.page_link` - navigation links between pages. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.page_link
- `st.checkbox` - boolean toggles. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.checkbox
- `st.toggle` - boolean switch UI. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.toggle
- `st.radio` - single selection from visible options. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.radio
- `st.selectbox` - single selection from larger option lists. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox
- `st.multiselect` - multi-selection. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect
- `st.pills` - compact selection pills. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.pills
- `st.segmented_control` - segmented option picker. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.segmented_control
- `st.slider` - numeric, date, or range selection. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.slider
- `st.select_slider` - slider across discrete values. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.select_slider
- `st.number_input` - numeric typed input. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.number_input
- `st.date_input` - date input. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.date_input
- `st.time_input` - time input. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.time_input
- `st.datetime_input` - datetime input. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.datetime_input
- `st.text_input` - short text input. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.text_input
- `st.text_area` - longer text input. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.text_area
- `st.chat_input` - chat prompt input. Official: https://docs.streamlit.io/develop/api-reference/chat/st.chat_input
- `st.file_uploader` - browser file uploads. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader
- `st.camera_input` - camera image capture. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.camera_input
- `st.audio_input` - audio capture input. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input
- `st.feedback` - thumb/star feedback capture. Official: https://docs.streamlit.io/develop/api-reference/widgets/st.feedback
- `st.columns` - horizontal layout. Official: https://docs.streamlit.io/develop/api-reference/layout/st.columns
- `st.container` - grouped layout block. Official: https://docs.streamlit.io/develop/api-reference/layout/st.container
- `st.empty` - placeholder replacement. Official: https://docs.streamlit.io/develop/api-reference/layout/st.empty
- `st.expander` - collapsible details. Official: https://docs.streamlit.io/develop/api-reference/layout/st.expander
- `st.popover` - button-triggered overlay container. Official: https://docs.streamlit.io/develop/api-reference/layout/st.popover
- `st.sidebar` - sidebar layout region. Official: https://docs.streamlit.io/develop/api-reference/layout/st.sidebar
- `st.tabs` - tabbed sections. Official: https://docs.streamlit.io/develop/api-reference/layout/st.tabs
- `st.form` - batched input submission. Official: https://docs.streamlit.io/develop/api-reference/execution-flow/st.form
- `st.form_submit_button` - form submission trigger. Official: https://docs.streamlit.io/develop/api-reference/execution-flow/st.form_submit_button
- `st.dialog` - modal interaction flow. Official: https://docs.streamlit.io/develop/api-reference/execution-flow/st.dialog
- `st.fragment` - isolated partial reruns. Official: https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment
- `st.stop` - early stop. Official: https://docs.streamlit.io/develop/api-reference/execution-flow/st.stop
- `st.rerun` - programmatic rerun. Official: https://docs.streamlit.io/develop/api-reference/execution-flow/st.rerun

## State Connections Navigation Auth

- `st.session_state` - per-session state across reruns. Official: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
- `st.cache_data` - cached data values and transformations. Official: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data
- `st.cache_resource` - cached singleton resources such as clients and models. Official: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource
- `st.query_params` - browser query parameters. Official: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.query_params
- `st.context` - browser/session context information. Official: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.context
- `st.secrets` - secret lookup. Official: https://docs.streamlit.io/develop/api-reference/connections/st.secrets
- `st.connection` - connection factory for external systems. Official: https://docs.streamlit.io/develop/api-reference/connections/st.connection
- `SQLConnection` - SQL query convenience connection. Official: https://docs.streamlit.io/develop/api-reference/connections/st.connections.sqlconnection
- `SnowflakeConnection` - Snowflake connection integration. Official: https://docs.streamlit.io/develop/api-reference/connections/st.connections.snowflakeconnection
- `BaseConnection` - base class for custom connections. Official: https://docs.streamlit.io/develop/api-reference/connections/st.connections.baseconnection
- `st.login` - start OIDC login flow. Official: https://docs.streamlit.io/develop/api-reference/user/st.login
- `st.logout` - clear logged-in user session. Official: https://docs.streamlit.io/develop/api-reference/user/st.logout
- `st.user` - read authenticated user info. Official: https://docs.streamlit.io/develop/api-reference/user/st.user
- `st.navigation` - programmatic multipage navigation. Official: https://docs.streamlit.io/develop/api-reference/navigation/st.navigation
- `st.Page` - page declaration for navigation. Official: https://docs.streamlit.io/develop/api-reference/navigation/st.page
- `st.switch_page` - programmatic page switch. Official: https://docs.streamlit.io/develop/api-reference/navigation/st.switch_page
- `st.set_page_config` - browser tab, layout, menu, and icon config. Official: https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config

## Routing guidance

- For beginner tutorials, use `references/app-architecture.md` and `references/recipes.md`.
- For weird rerun behavior, use `references/execution-state-and-reruns.md` before changing code.
- For broken widgets or duplicate widget key errors, use `references/widgets-forms-and-callbacks.md`.
- For slow apps, use `references/caching-connections-and-performance.md` and inspect where expensive work occurs.
- For uploaded files, downloads, images, audio, video, and generated artifacts, use `references/files-uploads-downloads-and-media.md`.
- For chatbots and RAG interfaces, use `references/llm-chat-and-rag-apps.md`.
- For production reviews, use `references/production-review-rubric.md`.
