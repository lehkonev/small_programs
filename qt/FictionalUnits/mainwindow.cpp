#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent):
    QMainWindow(parent),
    ui_(new Ui::MainWindow)
{
    ui_->setupUi(this);
    this->setWindowTitle(tr("Fictional Unit Converter and Timer"));
}

MainWindow::~MainWindow()
{
    delete ui_;
}
