/* Testing menu creation according to
 * https://doc.qt.io/qt-5/qtwidgets-mainwindows-menus-example.html
 */

#include "funitssettings.h"
#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <QMessageBox>
#include <QVBoxLayout>

MainWindow::MainWindow(QWidget *parent):
    QMainWindow(parent),
    ui_(new Ui::MainWindow)
{
    ui_->setupUi(this);
    this->setWindowTitle(FunitsSettings::instance()->getAppName());

    QWidget *widget = new QWidget;

    this->setCentralWidget(widget);

    QWidget *topFiller = new QWidget;
    topFiller->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);

    infoLabel = new QLabel(tr("<i>Choose a menu option &ndash; or right-click to "
                              "invoke a context menu</i> <sup>Aaaaaaaa</sup>"));
    infoLabel->setFrameStyle(QFrame::StyledPanel | QFrame::Sunken);
    infoLabel->setAlignment(Qt::AlignCenter);

    QWidget *bottomFiller = new QWidget;
    bottomFiller->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);

    QVBoxLayout *layout = new QVBoxLayout;
    layout->setMargin(5);
    layout->addWidget(topFiller);
    layout->addWidget(infoLabel);
    layout->addWidget(bottomFiller);
    widget->setLayout(layout);

    QString message = tr("A context menu is NOT available by right-clicking");
    statusBar()->showMessage(message);

    setMinimumSize(160, 160);
    resize(480, 320);

    //-------------------------------------------------------------------------
    // Create menu actions:
    QAction* reset_action = new QAction(tr("&Reset"), this);
    reset_action->setShortcut(tr("Ctrl+R"));
    reset_action->setStatusTip(tr("Reset the application’s fields."));
    connect(reset_action, &QAction::triggered, this, &MainWindow::reset);

    QAction* lang_en_action = new QAction(tr("&English"), this);
    lang_en_action->setCheckable(true);
    lang_en_action->setStatusTip(tr("Set the application’s language to English."));
    connect(lang_en_action, &QAction::triggered, this, &MainWindow::setLangEnglish);

    QAction* lang_fi_action = new QAction(tr("&Finnish"), this);
    lang_fi_action->setCheckable(true);
    lang_fi_action->setStatusTip(tr("Set the application’s language to Finnish."));
    connect(lang_fi_action, &QAction::triggered, this, &MainWindow::setLangFinnish);

    QActionGroup* lang_actions = new QActionGroup(this);
    lang_actions->addAction(lang_en_action);
    lang_actions->addAction(lang_fi_action);
    // The following should be read from a configuration file or something.
    lang_en_action->setChecked(true);

    QAction* exit_action = new QAction(tr("&Quit"), this);
    exit_action->setShortcut(tr("Ctrl+Q"));
    exit_action->setStatusTip(tr("Exit the application."));
    connect(exit_action, &QAction::triggered, this, &QWidget::close);

    QAction* about_action = new QAction(tr("&About…"), this);
    about_action->setStatusTip(tr("Show the About… window."));
    connect(about_action, &QAction::triggered, this, &MainWindow::about);

    //-------------------------------------------------------------------------
    // Create menus and put in the actions:
    QMenu* app_menu = ui_->menubar->addMenu(tr("&Application"));
    app_menu->addAction(reset_action);

    QMenu* lang_menu = app_menu->addMenu(tr("&Language"));
    lang_menu->addSeparator()->setText(tr("Languages"));
    lang_menu->addAction(lang_en_action);
    lang_menu->addAction(lang_fi_action);
    lang_menu->addSeparator();

    app_menu->addAction(exit_action);

    QMenu* help_menu = ui_->menubar->addMenu(tr("&Help"));
    help_menu->addAction(about_action);
}

MainWindow::~MainWindow()
{
    delete ui_;
}

void MainWindow::reset()
{
    infoLabel->setText(tr("Reset application’s values."));
}

void MainWindow::setLangEnglish()
{
    infoLabel->setText(tr("Set English."));
}

void MainWindow::setLangFinnish()
{
    infoLabel->setText(tr("Set Finnish."));
}

void MainWindow::about()
{
    infoLabel->setText(tr("Invoked <b>Help|About</b>"));
    QMessageBox::about(this,
            tr("About %1").arg(FunitsSettings::instance()->getAppName()),
            tr("Put some information here.\n"
               "This really doesn’t need to be modal."));
}
