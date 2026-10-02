from pathlib import Path

from PySide6.QtCore import (
    QObject,
    QThread,
    Signal,
    Qt,
)

from PySide6.QtGui import QColor

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QComboBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.analyzer import (
    MediaAnalyzer,
    MediaInfo,
)

from core.cancellation import (
    CancellationToken,
)

from core.download_queue import (
    DownloadQueue,
)

from core.download_task import (
    DownloadState,
    DownloadTask,
)

from core.queue_runner import (
    QueueRunner,
)

from services.ytdlp_service import (
    YTDLPService,
    DOWNLOAD_DIR,
)


# ============================================================
# Application Theme
# ============================================================

APP_STYLE = """
QMainWindow {
    background-color: #0d1117;
}

QScrollArea {
    background-color: #0d1117;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background-color: #0d1117;
}

QWidget {
    color: #e6edf3;
    font-family: "Segoe UI";
    font-size: 10pt;
}

QLabel#appTitle {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#appSubtitle {
    font-size: 10pt;
    color: #8b949e;
}

QLabel#sectionTitle {
    font-size: 12px;
    font-weight: 700;
    color: #f0f6fc;
}

QLabel#fieldLabel {
    font-size: 9pt;
    font-weight: 600;
    color: #aeb6c2;
}

QLabel#valueLabel {
    color: #e6edf3;
}

QFrame#card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
}

QLineEdit {
    background-color: #0d1117;
    color: #f0f6fc;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 0 12px;
    min-height: 42px;
    selection-background-color: #1f6feb;
}

QLineEdit:focus {
    border: 1px solid #388bfd;
}

QComboBox {
    background-color: #0d1117;
    color: #f0f6fc;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 0 12px;
    min-height: 42px;
}

QComboBox:hover {
    border: 1px solid #388bfd;
}

QComboBox::drop-down {
    width: 28px;
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #161b22;
    color: #f0f6fc;
    border: 1px solid #30363d;
    selection-background-color: #1f6feb;
}

QPushButton {
    background-color: #21262d;
    color: #f0f6fc;
    border: 1px solid #30363d;
    border-radius: 8px;
    min-height: 40px;
    padding: 0 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #30363d;
    border: 1px solid #484f58;
}

QPushButton:pressed {
    background-color: #161b22;
}

QPushButton:disabled {
    color: #6e7681;
    background-color: #161b22;
    border: 1px solid #21262d;
}

QPushButton#primaryButton {
    background-color: #1f6feb;
    border: 1px solid #388bfd;
    color: #ffffff;
}

QPushButton#primaryButton:hover {
    background-color: #388bfd;
}

QPushButton#primaryButton:pressed {
    background-color: #1158c7;
}

QPushButton#successButton {
    background-color: #238636;
    border: 1px solid #2ea043;
    color: #ffffff;
}

QPushButton#successButton:hover {
    background-color: #2ea043;
}

QPushButton#successButton:pressed {
    background-color: #196c2e;
}

QPushButton#dangerButton {
    background-color: #da3633;
    border: 1px solid #f85149;
    color: #ffffff;
}

QPushButton#dangerButton:hover {
    background-color: #f85149;
}

QPushButton#dangerButton:pressed {
    background-color: #b62324;
}

QProgressBar {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 7px;
    min-height: 16px;
    max-height: 16px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background-color: #1f6feb;
    border-radius: 6px;
}

QListWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 9px;
    padding: 5px;
    outline: none;
}

QListWidget::item {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    margin: 3px 1px;
    padding: 8px;
}

QListWidget::item:hover {
    background-color: #1c2128;
}

QListWidget::item:selected {
    background-color: #1c3b63;
    border: 1px solid #1f6feb;
}

QTextEdit {
    background-color: #0d1117;
    color: #b8c2cc;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 8px;
    font-family: "Cascadia Mono", "Consolas";
    font-size: 9pt;
}

QScrollBar:vertical {
    background: #0d1117;
    width: 10px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #484f58;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


# ============================================================
# Helper Functions
# ============================================================

def state_color(state: DownloadState) -> str:
    """Return a display color for a task state."""

    colors = {
        DownloadState.PENDING: "#8b949e",
        DownloadState.ANALYZING: "#d29922",
        DownloadState.DOWNLOADING: "#58a6ff",
        DownloadState.PROCESSING: "#bc8cff",
        DownloadState.COMPLETED: "#3fb950",
        DownloadState.FAILED: "#f85149",
        DownloadState.CANCELLED: "#f0883e",
    }

    return colors.get(
        state,
        "#8b949e",
    )


def state_icon(state: DownloadState) -> str:
    """Return a simple text icon for a task state."""

    icons = {
        DownloadState.PENDING: "○",
        DownloadState.ANALYZING: "◌",
        DownloadState.DOWNLOADING: "↓",
        DownloadState.PROCESSING: "⚙",
        DownloadState.COMPLETED: "✓",
        DownloadState.FAILED: "!",
        DownloadState.CANCELLED: "■",
    }

    return icons.get(
        state,
        "•",
    )


# ============================================================
# Background Worker
# ============================================================

class Worker(QObject):
    """
    Runs long-running operations away from the GUI thread.
    """

    finished = Signal()

    success = Signal(object)

    error = Signal(str)

    progress = Signal(int, str)

    task_update = Signal(object)

    def __init__(
        self,
        operation: str,
        service=None,
        analyzer=None,
        queue=None,
        **kwargs,
    ):
        super().__init__()

        self.operation = operation
        self.service = service
        self.analyzer = analyzer
        self.queue = queue
        self.kwargs = kwargs

        self.cancellation_token = (
            CancellationToken()
        )

    def run(self):

        try:

            # ------------------------------------------------
            # Analyze
            # ------------------------------------------------

            if self.operation == "analyze":

                if self.analyzer is None:
                    raise RuntimeError(
                        "MediaAnalyzer is not initialized."
                    )

                result = self.analyzer.analyze(
                    self.kwargs["url"]
                )

                self.success.emit(
                    result
                )

            # ------------------------------------------------
            # Queue
            # ------------------------------------------------

            elif self.operation == "queue":

                if self.service is None:
                    raise RuntimeError(
                        "YTDLPService is not initialized."
                    )

                if self.queue is None:
                    raise RuntimeError(
                        "DownloadQueue is not initialized."
                    )

                runner = QueueRunner(
                    service=self.service,
                    queue=self.queue,
                    task_callback=(
                        self.task_update.emit
                    ),
                    progress_callback=(
                        self.progress.emit
                    ),
                    cancellation_token=(
                        self.cancellation_token
                    ),
                )

                result = runner.run()

                self.success.emit(
                    result
                )

            else:

                raise ValueError(
                    f"Unknown worker operation: "
                    f"{self.operation}"
                )

        except Exception as exc:

            self.error.emit(
                str(exc)
            )

        finally:

            self.finished.emit()

    def cancel(self):
        """Request cancellation."""

        self.cancellation_token.cancel()


# ============================================================
# Main Window
# ============================================================

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Video Downloader"
        )

        self.resize(
            980,
            820,
        )

        self.setMinimumSize(
            860,
            680,
        )

        # ----------------------------------------------------
        # Backend
        # ----------------------------------------------------

        self.service = None

        self.analyzer = None

        self.queue = DownloadQueue()

        self.info = None

        # ----------------------------------------------------
        # Worker
        # ----------------------------------------------------

        self.thread = None

        self.worker = None

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        self.setup_ui()

        self.initialize_backend()

    # ========================================================
    # Backend Initialization
    # ========================================================

    def initialize_backend(self):

        try:

            self.service = YTDLPService()

            self.analyzer = MediaAnalyzer(
                self.service
            )

            self.set_status(
                "Ready",
                "#3fb950",
            )

            self.log(
                "Application initialized."
            )

        except Exception as exc:

            self.set_status(
                "Dependency Error",
                "#f85149",
            )

            self.set_all_controls_enabled(
                False
            )

            self.show_message_box(
                "Initialization Error",
                str(exc),
                QMessageBox.Critical,
            )

    # ========================================================
    # UI Setup
    # ========================================================

    def setup_ui(self):

        # ----------------------------------------------------
        # Scroll Area
        # ----------------------------------------------------

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.setCentralWidget(
            scroll
        )

        content = QWidget()

        scroll.setWidget(
            content
        )

        root = QVBoxLayout(
            content
        )

        root.setContentsMargins(
            20,
            18,
            20,
            20,
        )

        root.setSpacing(
            10
        )

        # ====================================================
        # Header
        # ====================================================

        header = QHBoxLayout()

        header.setSpacing(
            12
        )

        title_layout = QVBoxLayout()

        title_layout.setSpacing(
            2
        )

        title = QLabel(
            "Video Downloader"
        )

        title.setObjectName(
            "appTitle"
        )

        subtitle = QLabel(
            "Simple and fast desktop media downloader"
        )

        subtitle.setObjectName(
            "appSubtitle"
        )

        title_layout.addWidget(
            title
        )

        title_layout.addWidget(
            subtitle
        )

        header.addLayout(
            title_layout
        )

        header.addStretch()

        version = QLabel(
            "V1"
        )

        version.setAlignment(
            Qt.AlignCenter
        )

        version.setFixedSize(
            62,
            52,
        )

        version.setStyleSheet(
            """
            background-color: #1c3b63;
            color: #58a6ff;
            border: 1px solid #1f6feb;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 700;
            """
        )

        header.addWidget(
            version
        )

        root.addLayout(
            header
        )

        # ====================================================
        # URL Card
        # ====================================================

        url_card = self.create_card()

        url_layout = QVBoxLayout(
            url_card
        )

        url_layout.setContentsMargins(
            16,
            13,
            16,
            13,
        )

        url_layout.setSpacing(
            8
        )

        url_title = QLabel(
            "Video URL"
        )

        url_title.setObjectName(
            "sectionTitle"
        )

        url_layout.addWidget(
            url_title
        )

        url_row = QHBoxLayout()

        url_row.setSpacing(
            10
        )

        self.url_input = QLineEdit()

        self.url_input.setPlaceholderText(
            "Paste a supported video URL..."
        )

        self.url_input.returnPressed.connect(
            self.analyze
        )

        self.analyze_button = QPushButton(
            "⟳  Analyze"
        )

        self.analyze_button.setObjectName(
            "primaryButton"
        )

        self.analyze_button.setFixedWidth(
            125
        )

        self.analyze_button.clicked.connect(
            self.analyze
        )

        url_row.addWidget(
            self.url_input,
            1,
        )

        url_row.addWidget(
            self.analyze_button
        )

        url_layout.addLayout(
            url_row
        )

        root.addWidget(
            url_card
        )

        # ====================================================
        # Media Information Card
        # ====================================================

        info_card = self.create_card()

        info_layout = QVBoxLayout(
            info_card
        )

        info_layout.setContentsMargins(
            16,
            13,
            16,
            13,
        )

        info_layout.setSpacing(
            8
        )

        info_title = QLabel(
            "Media Information"
        )

        info_title.setObjectName(
            "sectionTitle"
        )

        info_layout.addWidget(
            info_title
        )

        form = QFormLayout()

        form.setHorizontalSpacing(
            20
        )

        form.setVerticalSpacing(
            6
        )

        self.title_label = QLabel(
            "—"
        )

        self.title_label.setObjectName(
            "valueLabel"
        )

        self.title_label.setWordWrap(
            True
        )

        self.title_label.setMaximumHeight(
            42
        )

        self.duration_label = QLabel(
            "—"
        )

        self.duration_label.setObjectName(
            "valueLabel"
        )

        self.source_label = QLabel(
            "—"
        )

        self.source_label.setObjectName(
            "valueLabel"
        )

        form.addRow(
            "Title:",
            self.title_label,
        )

        form.addRow(
            "Duration:",
            self.duration_label,
        )

        form.addRow(
            "Source:",
            self.source_label,
        )

        info_layout.addLayout(
            form
        )

        root.addWidget(
            info_card
        )

        # ====================================================
        # Options Card
        # ====================================================

        options_card = self.create_card()

        options_layout = QGridLayout(
            options_card
        )

        options_layout.setContentsMargins(
            16,
            13,
            16,
            13,
        )

        options_layout.setHorizontalSpacing(
            12
        )

        options_layout.setVerticalSpacing(
            6
        )

        # ----------------------------------------------------
        # Quality
        # ----------------------------------------------------

        quality_label = QLabel(
            "Video Quality"
        )

        quality_label.setObjectName(
            "fieldLabel"
        )

        self.quality_combo = QComboBox()

        self.quality_combo.addItem(
            "Analyze a URL first",
            None,
        )

        self.quality_combo.setEnabled(
            False
        )

        options_layout.addWidget(
            quality_label,
            0,
            0,
        )

        options_layout.addWidget(
            self.quality_combo,
            1,
            0,
        )

        # ----------------------------------------------------
        # Output Format
        # ----------------------------------------------------

        format_label = QLabel(
            "Output Format"
        )

        format_label.setObjectName(
            "fieldLabel"
        )

        self.format_combo = QComboBox()

        self.format_combo.addItems([
            "MP4",
            "MKV",
        ])

        self.format_combo.setEnabled(
            False
        )

        options_layout.addWidget(
            format_label,
            0,
            1,
        )

        options_layout.addWidget(
            self.format_combo,
            1,
            1,
        )

        # ----------------------------------------------------
        # Save Location
        # ----------------------------------------------------

        save_label = QLabel(
            "Save Location"
        )

        save_label.setObjectName(
            "fieldLabel"
        )

        save_row = QHBoxLayout()

        save_row.setSpacing(
            8
        )

        self.output_input = QLineEdit(
            str(DOWNLOAD_DIR)
        )

        self.output_input.setToolTip(
            str(
                Path(
                    DOWNLOAD_DIR
                ).resolve()
            )
        )

        self.output_input.setCursorPosition(
            0
        )

        self.browse_button = QPushButton(
            "📁  Browse"
        )

        self.browse_button.setFixedWidth(
            110
        )

        self.browse_button.clicked.connect(
            self.choose_directory
        )

        save_row.addWidget(
            self.output_input,
            1,
        )

        save_row.addWidget(
            self.browse_button
        )

        options_layout.addWidget(
            save_label,
            0,
            2,
        )

        options_layout.addLayout(
            save_row,
            1,
            2,
        )

        options_layout.setColumnStretch(
            0,
            1,
        )

        options_layout.setColumnStretch(
            1,
            1,
        )

        options_layout.setColumnStretch(
            2,
            2,
        )

        root.addWidget(
            options_card
        )

        # ====================================================
        # Download Queue Card
        # ====================================================

        queue_card = self.create_card()

        queue_layout = QVBoxLayout(
            queue_card
        )

        queue_layout.setContentsMargins(
            16,
            13,
            16,
            13,
        )

        queue_layout.setSpacing(
            8
        )

        # Header

        queue_header = QHBoxLayout()

        queue_title = QLabel(
            "Download Queue"
        )

        queue_title.setObjectName(
            "sectionTitle"
        )

        self.queue_count_label = QLabel(
            "0 tasks"
        )

        self.queue_count_label.setStyleSheet(
            """
            color: #8b949e;
            font-weight: 600;
            """
        )

        queue_header.addWidget(
            queue_title
        )

        queue_header.addStretch()

        queue_header.addWidget(
            self.queue_count_label
        )

        queue_layout.addLayout(
            queue_header
        )

        # Queue list

        self.queue_list = QListWidget()

        self.queue_list.setFixedHeight(
            125
        )

        self.queue_list.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )

        queue_layout.addWidget(
            self.queue_list
        )

        # Queue buttons

        controls = QHBoxLayout()

        controls.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        controls.setSpacing(
            10
        )

        self.add_queue_button = QPushButton(
            "＋  Add to Queue"
        )

        self.add_queue_button.setFixedSize(
            150,
            40,
        )

        self.add_queue_button.setEnabled(
            False
        )

        self.add_queue_button.clicked.connect(
            self.add_to_queue
        )

        self.remove_queue_button = QPushButton(
            "×  Remove"
        )

        self.remove_queue_button.setFixedSize(
            120,
            40,
        )

        self.remove_queue_button.clicked.connect(
            self.remove_selected_task
        )

        self.start_queue_button = QPushButton(
            "▶  Start Queue"
        )

        self.start_queue_button.setObjectName(
            "successButton"
        )

        self.start_queue_button.setFixedSize(
            145,
            40,
        )

        self.start_queue_button.setEnabled(
            False
        )

        self.start_queue_button.clicked.connect(
            self.start_queue
        )

        self.cancel_queue_button = QPushButton(
            "■  Cancel"
        )

        self.cancel_queue_button.setObjectName(
            "dangerButton"
        )

        self.cancel_queue_button.setFixedSize(
            120,
            40,
        )

        self.cancel_queue_button.setEnabled(
            False
        )

        self.cancel_queue_button.clicked.connect(
            self.cancel_queue
        )

        controls.addWidget(
            self.add_queue_button
        )

        controls.addWidget(
            self.remove_queue_button
        )

        controls.addStretch(
            1
        )

        controls.addWidget(
            self.start_queue_button
        )

        controls.addWidget(
            self.cancel_queue_button
        )

        queue_layout.addLayout(
            controls
        )

        root.addWidget(
            queue_card
        )

        # ====================================================
        # Current Task Card
        # ====================================================

        progress_card = self.create_card()

        progress_layout = QVBoxLayout(
            progress_card
        )

        progress_layout.setContentsMargins(
            16,
            11,
            16,
            11,
        )

        progress_layout.setSpacing(
            7
        )

        progress_header = QHBoxLayout()

        progress_title = QLabel(
            "Current Task"
        )

        progress_title.setObjectName(
            "sectionTitle"
        )

        self.progress_percent_label = QLabel(
            "0%"
        )

        self.progress_percent_label.setStyleSheet(
            """
            color: #58a6ff;
            font-weight: 700;
            """
        )

        progress_header.addWidget(
            progress_title
        )

        progress_header.addStretch()

        progress_header.addWidget(
            self.progress_percent_label
        )

        progress_layout.addLayout(
            progress_header
        )

        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(
            0,
            100,
        )

        self.progress_bar.setValue(
            0
        )

        progress_layout.addWidget(
            self.progress_bar
        )

        self.status_label = QLabel(
            "Initializing..."
        )

        self.status_label.setWordWrap(
            True
        )

        progress_layout.addWidget(
            self.status_label
        )

        root.addWidget(
            progress_card
        )

        # ====================================================
        # Activity Log Card
        # ====================================================

        log_card = self.create_card()

        log_layout = QVBoxLayout(
            log_card
        )

        log_layout.setContentsMargins(
            16,
            11,
            16,
            11,
        )

        log_layout.setSpacing(
            7
        )

        log_title = QLabel(
            "Activity Log"
        )

        log_title.setObjectName(
            "sectionTitle"
        )

        log_layout.addWidget(
            log_title
        )

        self.log_output = QTextEdit()

        self.log_output.setReadOnly(
            True
        )

        self.log_output.setFixedHeight(
            90
        )

        log_layout.addWidget(
            self.log_output
        )

        root.addWidget(
            log_card
        )

        root.addSpacing(
            8
        )

        # Show initial queue state.

        self.refresh_queue()

    # ========================================================
    # Card Helper
    # ========================================================

    @staticmethod
    def create_card():

        card = QFrame()

        card.setObjectName(
            "card"
        )

        return card

    # ========================================================
    # Analyze
    # ========================================================

    def analyze(self):

        url = (
            self.url_input
            .text()
            .strip()
        )

        if not url:

            self.show_message_box(
                "Invalid URL",
                "Please enter a video URL.",
                QMessageBox.Warning,
            )

            return

        if self.analyzer is None:

            self.show_message_box(
                "Error",
                "Media analyzer is not initialized.",
                QMessageBox.Critical,
            )

            return

        self.info = None

        self.title_label.setText(
            "Analyzing..."
        )

        self.duration_label.setText(
            "—"
        )

        self.source_label.setText(
            "—"
        )

        self.quality_combo.clear()

        self.quality_combo.addItem(
            "Analyzing...",
            None,
        )

        self.quality_combo.setEnabled(
            False
        )

        self.format_combo.setEnabled(
            False
        )

        self.add_queue_button.setEnabled(
            False
        )

        self.progress_bar.setValue(
            0
        )

        self.progress_percent_label.setText(
            "0%"
        )

        self.set_status(
            "Analyzing media...",
            "#d29922",
        )

        self.log_output.clear()

        self.log(
            f"Analyzing: {url}"
        )

        self.set_controls_for_operation(
            True
        )

        self.start_worker(
            "analyze",
            url=url,
        )

    # ========================================================
    # Analysis Result
    # ========================================================

    def handle_analysis_result(
        self,
        media_info: MediaInfo,
    ):

        self.info = (
            media_info.raw_info
        )

        self.title_label.setText(
            media_info.title
        )

        self.duration_label.setText(
            self.format_duration(
                media_info.duration
            )
        )

        self.source_label.setText(
            media_info.source
        )

        from core.format_manager import (
            get_available_resolutions,
        )

        resolutions = (
            get_available_resolutions(
                self.info
            )
        )

        self.quality_combo.clear()

        self.quality_combo.addItem(
            "Best available",
            None,
        )

        for resolution in resolutions:

            self.quality_combo.addItem(
                f"{resolution}p",
                resolution,
            )

        self.quality_combo.setEnabled(
            bool(resolutions)
        )

        self.format_combo.setEnabled(
            True
        )

        self.add_queue_button.setEnabled(
            True
        )

        self.analyze_button.setEnabled(
            True
        )

        self.browse_button.setEnabled(
            True
        )

        self.set_status(
            "Analysis complete",
            "#3fb950",
        )

        self.log(
            f"Title: {media_info.title}"
        )

        self.log(
            f"Duration: "
            f"{self.format_duration(media_info.duration)}"
        )

        self.log(
            f"Source: {media_info.source}"
        )

        self.log(
            f"Formats found: "
            f"{media_info.format_count}"
        )

        self.log(
            "Ready to add this task to the queue."
        )

    # ========================================================
    # Add To Queue
    # ========================================================

    def add_to_queue(self):

        if not self.info:

            self.show_message_box(
                "No Media",
                "Please analyze the URL first.",
                QMessageBox.Warning,
            )

            return

        url = (
            self.url_input
            .text()
            .strip()
        )

        if not url:
            return

        output_dir = (
            self.output_input
            .text()
            .strip()
        )

        if not output_dir:

            self.show_message_box(
                "Output Folder",
                "Please select an output folder.",
                QMessageBox.Warning,
            )

            return

        max_height = (
            self.quality_combo
            .currentData()
        )

        output_format = (
            self.format_combo
            .currentText()
            .lower()
        )

        task = DownloadTask(
            url=url,
            output_dir=output_dir,
            output_format=output_format,
            max_height=max_height,
        )

        task.title = self.info.get(
            "title",
            "Unknown",
        )

        self.queue.add(
            task
        )

        self.refresh_queue()

        self.start_queue_button.setEnabled(
            self.queue.has_pending()
        )

        quality_text = (
            f"{max_height}p"
            if max_height
            else "Best"
        )

        self.log(
            f"Added: {task.title}"
        )

        self.log(
            f"Quality: {quality_text} | "
            f"Format: {output_format.upper()}"
        )

        self.set_status(
            "Task added to queue",
            "#3fb950",
        )

        # Reset current URL.

        self.url_input.clear()

        self.info = None

        self.title_label.setText(
            "—"
        )

        self.duration_label.setText(
            "—"
        )

        self.source_label.setText(
            "—"
        )

        self.quality_combo.clear()

        self.quality_combo.addItem(
            "Analyze a URL first",
            None,
        )

        self.quality_combo.setEnabled(
            False
        )

        self.format_combo.setEnabled(
            False
        )

        self.add_queue_button.setEnabled(
            False
        )

    # ========================================================
    # Remove Selected Task
    # ========================================================

    def remove_selected_task(self):

        row = (
            self.queue_list
            .currentRow()
        )

        if row < 0:

            self.show_message_box(
                "Queue",
                "Select a task first.",
                QMessageBox.Information,
            )

            return

        tasks = (
            self.queue.all_tasks()
        )

        if row >= len(tasks):
            return

        task = tasks[row]

        if (
            task.state
            != DownloadState.PENDING
        ):

            self.show_message_box(
                "Task",
                "Only pending tasks can be removed.",
                QMessageBox.Information,
            )

            return

        self.queue.remove(
            task
        )

        self.refresh_queue()

        self.start_queue_button.setEnabled(
            self.queue.has_pending()
        )

        self.log(
            f"Removed: {task.title}"
        )

    # ========================================================
    # Start Queue
    # ========================================================

    def start_queue(self):

        if not self.queue.has_pending():

            self.show_message_box(
                "Queue",
                "There are no pending tasks.",
                QMessageBox.Information,
            )

            return

        if self.service is None:

            self.show_message_box(
                "Error",
                "Downloader service is not initialized.",
                QMessageBox.Critical,
            )

            return

        self.progress_bar.setValue(
            0
        )

        self.progress_percent_label.setText(
            "0%"
        )

        self.set_status(
            "Starting download queue...",
            "#58a6ff",
        )

        self.log(
            "Download queue started."
        )

        self.start_queue_button.setEnabled(
            False
        )

        self.add_queue_button.setEnabled(
            False
        )

        self.remove_queue_button.setEnabled(
            False
        )

        self.analyze_button.setEnabled(
            False
        )

        self.browse_button.setEnabled(
            False
        )

        self.quality_combo.setEnabled(
            False
        )

        self.format_combo.setEnabled(
            False
        )

        self.cancel_queue_button.setEnabled(
            True
        )

        self.start_worker(
            "queue"
        )

    # ========================================================
    # Cancel Queue
    # ========================================================

    def cancel_queue(self):

        if self.worker is None:
            return

        self.set_status(
            "Cancelling...",
            "#f0883e",
        )

        self.log(
            "Cancellation requested."
        )

        self.cancel_queue_button.setEnabled(
            False
        )

        self.worker.cancel()

    # ========================================================
    # Task Update
    # ========================================================

    def handle_task_update(
        self,
        task: DownloadTask,
    ):

        self.refresh_queue()

        state = task.state

        if state == DownloadState.ANALYZING:

            self.set_status(
                f"Analyzing: {task.title}",
                state_color(state),
            )

            self.progress_bar.setValue(
                0
            )

            self.progress_percent_label.setText(
                "0%"
            )

        elif state == DownloadState.DOWNLOADING:

            self.set_status(
                f"Downloading: {task.title}",
                state_color(state),
            )

        elif state == DownloadState.PROCESSING:

            self.set_status(
                f"Processing: {task.title}",
                state_color(state),
            )

        elif state == DownloadState.COMPLETED:

            self.progress_bar.setValue(
                100
            )

            self.progress_percent_label.setText(
                "100%"
            )

            self.set_status(
                f"Completed: {task.title}",
                state_color(state),
            )

        elif state == DownloadState.FAILED:

            self.set_status(
                f"Failed: {task.title}",
                state_color(state),
            )

            if task.error:

                self.log(
                    f"Error: {task.error}"
                )

        elif state == DownloadState.CANCELLED:

            self.set_status(
                f"Cancelled: {task.title}",
                state_color(state),
            )

        self.update_queue_count()

    # ========================================================
    # Queue Rendering
    # ========================================================

    def refresh_queue(self):

        self.queue_list.clear()

        tasks = (
            self.queue.all_tasks()
        )

        # ----------------------------------------------------
        # Empty Queue
        # ----------------------------------------------------

        if not tasks:

            item = QListWidgetItem(
                "＋\nNo tasks in queue"
            )

            item.setTextAlignment(
                Qt.AlignCenter
            )

            item.setForeground(
                QColor(
                    "#6e7681"
                )
            )

            self.queue_list.addItem(
                item
            )

            self.update_queue_count()

            return

        # ----------------------------------------------------
        # Render Tasks
        # ----------------------------------------------------

        for index, task in enumerate(tasks):

            state = task.state

            quality = (
                f"{task.max_height}p"
                if task.max_height
                else "Best"
            )

            icon = state_icon(
                state
            )

            text = (
                f"{icon}  "
                f"{index + 1}. "
                f"{task.title}\n"
                f"{task.output_format.upper()} "
                f" • {quality} "
                f" • {state.value}"
            )

            if task.error:

                text += (
                    f"\nError: {task.error}"
                )

            item = QListWidgetItem(
                text
            )

            item.setForeground(
                QColor(
                    state_color(
                        state
                    )
                )
            )

            item.setToolTip(
                task.url
            )

            self.queue_list.addItem(
                item
            )

        self.update_queue_count()

    # ========================================================
    # Queue Count
    # ========================================================

    def update_queue_count(self):

        count = len(
            self.queue
        )

        if count == 1:

            text = "1 task"

        else:

            text = f"{count} tasks"

        self.queue_count_label.setText(
            text
        )

    # ========================================================
    # Worker Start
    # ========================================================

    def start_worker(
        self,
        operation: str,
        **kwargs,
    ):

        if (
            self.thread is not None
            and self.thread.isRunning()
        ):

            self.show_message_box(
                "Busy",
                "Another operation is already running.",
                QMessageBox.Warning,
            )

            return

        if self.service is None:

            self.show_message_box(
                "Error",
                "Downloader service is not initialized.",
                QMessageBox.Critical,
            )

            return

        self.thread = QThread(
            self
        )

        self.worker = Worker(
            operation=operation,
            service=self.service,
            analyzer=self.analyzer,
            queue=self.queue,
            **kwargs,
        )

        self.worker.moveToThread(
            self.thread
        )

        # Start

        self.thread.started.connect(
            self.worker.run
        )

        # Signals

        self.worker.success.connect(
            self.operation_success
        )

        self.worker.error.connect(
            self.operation_error
        )

        self.worker.progress.connect(
            self.update_progress
        )

        self.worker.task_update.connect(
            self.handle_task_update
        )

        # Cleanup

        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.finished.connect(
            self.worker_finished
        )

        self.thread.start()

    # ========================================================
    # Operation Success
    # ========================================================

    def operation_success(
        self,
        result,
    ):

        # ----------------------------------------------------
        # Analysis
        # ----------------------------------------------------

        if isinstance(
            result,
            MediaInfo,
        ):

            self.handle_analysis_result(
                result
            )

            return

        # ----------------------------------------------------
        # Queue
        # ----------------------------------------------------

        if isinstance(
            result,
            dict,
        ):

            completed = result.get(
                "completed",
                0,
            )

            failed = result.get(
                "failed",
                0,
            )

            cancelled = result.get(
                "cancelled",
                0,
            )

            self.refresh_queue()

            if cancelled > 0:

                self.set_status(
                    "Queue cancelled",
                    "#f0883e",
                )

                self.log(
                    "Queue cancelled."
                )

                self.show_message_box(
                    "Queue Cancelled",
                    (
                        f"Completed: {completed}\n"
                        f"Failed: {failed}\n"
                        f"Cancelled: {cancelled}"
                    ),
                    QMessageBox.Information,
                )

            else:

                self.progress_bar.setValue(
                    100
                )

                self.progress_percent_label.setText(
                    "100%"
                )

                self.set_status(
                    "Queue completed",
                    "#3fb950",
                )

                self.log(
                    "Queue completed."
                )

                self.show_message_box(
                    "Queue Complete",
                    (
                        f"Completed: {completed}\n"
                        f"Failed: {failed}"
                    ),
                    QMessageBox.Information,
                )

    # ========================================================
    # Operation Error
    # ========================================================

    def operation_error(
        self,
        message: str,
    ):

        self.set_status(
            "Operation failed",
            "#f85149",
        )

        self.log(
            "ERROR:"
        )

        self.log(
            message
        )

        self.show_message_box(
            "Error",
            message,
            QMessageBox.Critical,
        )

    # ========================================================
    # Worker Finished
    # ========================================================

    def worker_finished(self):

        self.thread = None

        self.worker = None

        self.cancel_queue_button.setEnabled(
            False
        )

        self.analyze_button.setEnabled(
            True
        )

        self.browse_button.setEnabled(
            True
        )

        self.remove_queue_button.setEnabled(
            True
        )

        self.start_queue_button.setEnabled(
            self.queue.has_pending()
        )

        self.quality_combo.setEnabled(
            self.info is not None
        )

        self.format_combo.setEnabled(
            self.info is not None
        )

        self.add_queue_button.setEnabled(
            self.info is not None
        )

    # ========================================================
    # Progress
    # ========================================================

    def update_progress(
        self,
        value: int,
        message: str,
    ):

        value = max(
            0,
            min(
                100,
                int(value),
            ),
        )

        # Same numeric value is used for both elements.

        self.progress_bar.setValue(
            value
        )

        self.progress_percent_label.setText(
            f"{value}%"
        )

        self.set_status(
            message,
            "#58a6ff",
        )

    # ========================================================
    # Status
    # ========================================================

    def set_status(
        self,
        message: str,
        color: str,
    ):

        self.status_label.setText(
            message
        )

        self.status_label.setStyleSheet(
            f"""
            color: {color};
            font-weight: 600;
            """
        )

    # ========================================================
    # Message Box
    # ========================================================

    def show_message_box(
        self,
        title: str,
        message: str,
        icon=QMessageBox.Information,
    ):
        """
        Display a readable dark-themed QMessageBox.

        This avoids the previous problem where the application
        dark stylesheet caused QMessageBox text to become
        almost invisible.
        """

        box = QMessageBox(
            self
        )

        box.setWindowTitle(
            title
        )

        box.setIcon(
            icon
        )

        box.setText(
            message
        )

        box.setStandardButtons(
            QMessageBox.Ok
        )

        box.setStyleSheet(
            """
            QMessageBox {
                background-color: #161b22;
            }

            QMessageBox QLabel {
                color: #f0f6fc;
                font-size: 10pt;
                min-width: 320px;
            }

            QMessageBox QPushButton {
                background-color: #21262d;
                color: #f0f6fc;
                border: 1px solid #30363d;
                border-radius: 7px;
                padding: 7px 22px;
                min-width: 80px;
                min-height: 32px;
            }

            QMessageBox QPushButton:hover {
                background-color: #30363d;
            }

            QMessageBox QPushButton:pressed {
                background-color: #161b22;
            }
            """
        )

        box.exec()

    # ========================================================
    # Directory Selection
    # ========================================================

    def choose_directory(self):

        current_path = Path(
            self.output_input
            .text()
            .strip()
        )

        directory = (
            QFileDialog
            .getExistingDirectory(
                self,
                "Select Download Folder",
                str(
                    current_path.resolve()
                ),
            )
        )

        if directory:

            self.output_input.setText(
                directory
            )

            self.output_input.setToolTip(
                directory
            )

            self.output_input.setCursorPosition(
                0
            )

            self.log(
                f"Output directory: {directory}"
            )

    # ========================================================
    # Control State
    # ========================================================

    def set_controls_for_operation(
        self,
        busy: bool,
    ):

        self.analyze_button.setEnabled(
            not busy
        )

        self.browse_button.setEnabled(
            not busy
        )

        self.remove_queue_button.setEnabled(
            not busy
        )

        self.start_queue_button.setEnabled(
            not busy
            and self.queue.has_pending()
        )

        self.cancel_queue_button.setEnabled(
            False
        )

        self.add_queue_button.setEnabled(
            not busy
            and self.info is not None
        )

        self.quality_combo.setEnabled(
            not busy
            and self.info is not None
        )

        self.format_combo.setEnabled(
            not busy
            and self.info is not None
        )

    def set_all_controls_enabled(
        self,
        enabled: bool,
    ):

        self.analyze_button.setEnabled(
            enabled
        )

        self.browse_button.setEnabled(
            enabled
        )

        self.remove_queue_button.setEnabled(
            enabled
        )

        self.start_queue_button.setEnabled(
            enabled
            and self.queue.has_pending()
        )

        self.cancel_queue_button.setEnabled(
            False
        )

        self.add_queue_button.setEnabled(
            enabled
            and self.info is not None
        )

        self.quality_combo.setEnabled(
            enabled
            and self.info is not None
        )

        self.format_combo.setEnabled(
            enabled
            and self.info is not None
        )

    # ========================================================
    # Logging
    # ========================================================

    def log(
        self,
        message: str,
    ):

        self.log_output.append(
            message
        )

        scrollbar = (
            self.log_output
            .verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.maximum()
        )

    # ========================================================
    # Duration
    # ========================================================

    @staticmethod
    def format_duration(
        seconds,
    ):

        if seconds is None:
            return "Unknown"

        try:
            seconds = int(seconds)
        except (TypeError, ValueError):
            return "Unknown"

        hours, remainder = divmod(
            seconds,
            3600,
        )

        minutes, seconds = divmod(
            remainder,
            60,
        )

        if hours:

            return (
                f"{hours:02}:"
                f"{minutes:02}:"
                f"{seconds:02}"
            )

        return (
            f"{minutes:02}:"
            f"{seconds:02}"
        )

    # ========================================================
    # Close Event
    # ========================================================

    def closeEvent(
        self,
        event,
    ):

        if (
            self.worker is not None
            and self.thread is not None
            and self.thread.isRunning()
        ):

            reply = QMessageBox.question(
                self,
                "Download in Progress",
                (
                    "A download operation is still running.\n\n"
                    "Do you want to cancel it and exit?"
                ),
                (
                    QMessageBox.Yes
                    | QMessageBox.No
                ),
                QMessageBox.No,
            )

            if reply == QMessageBox.No:

                event.ignore()

                return

            self.worker.cancel()

            self.set_status(
                "Cancelling before exit...",
                "#f0883e",
            )

            event.ignore()

            return

        event.accept()


# ============================================================
# Application Entry
# ============================================================

def main():

    app = QApplication([])

    app.setApplicationName(
        "Video Downloader"
    )

    app.setOrganizationName(
        "Video Downloader"
    )

    app.setStyleSheet(
        APP_STYLE
    )

    window = MainWindow()

    window.show()

    app.exec()


if __name__ == "__main__":
    main()