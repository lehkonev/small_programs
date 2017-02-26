#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    connect(ui->pituus_kentta_hex, SIGNAL(editingFinished()), this, SLOT(pituus()));
    connect(ui->pituus_kentta_sk, SIGNAL(editingFinished()), this, SLOT(pituus()));
    connect(ui->pituus_kentta_si, SIGNAL(editingFinished()), this, SLOT(pituus()));
    connect(ui->pituus_valinta_sk, SIGNAL(currentIndexChanged(int)), this, SLOT(pituus()));
    connect(ui->pituus_valinta_si, SIGNAL(currentIndexChanged(int)), this, SLOT(pituus()));

    connect(ui->nopeus_kentta_hex, SIGNAL(editingFinished()), this, SLOT(nopeus()));
    connect(ui->nopeus_kentta_sk, SIGNAL(editingFinished()), this, SLOT(nopeus()));
    connect(ui->nopeus_kentta_si, SIGNAL(editingFinished()), this, SLOT(nopeus()));
    connect(ui->nopeus_valinta_sk, SIGNAL(currentIndexChanged(int)), this, SLOT(nopeus()));
    connect(ui->nopeus_valinta_si, SIGNAL(currentIndexChanged(int)), this, SLOT(nopeus()));

    connect(ui->paino_kentta_hex, SIGNAL(editingFinished()), this, SLOT(paino()));
    connect(ui->paino_kentta_sk, SIGNAL(editingFinished()), this, SLOT(paino()));
    connect(ui->paino_kentta_si, SIGNAL(editingFinished()), this, SLOT(paino()));
    connect(ui->paino_valinta_sk, SIGNAL(currentIndexChanged(int)), this, SLOT(paino()));
    connect(ui->paino_valinta_si, SIGNAL(currentIndexChanged(int)), this, SLOT(paino()));

    connect(ui->lampo_kentta_hex, SIGNAL(editingFinished()), this, SLOT(lampo()));
    connect(ui->lampo_kentta_sk, SIGNAL(editingFinished()), this, SLOT(lampo()));
    connect(ui->lampo_kentta_si, SIGNAL(editingFinished()), this, SLOT(lampo()));
    connect(ui->lampo_valinta_sk, SIGNAL(currentIndexChanged(int)), this, SLOT(lampo()));
    connect(ui->lampo_valinta_si, SIGNAL(currentIndexChanged(int)), this, SLOT(lampo()));

    connect(ui->sahko_kentta_hex, SIGNAL(editingFinished()), this, SLOT(sahko()));
    connect(ui->sahko_kentta_sk, SIGNAL(editingFinished()), this, SLOT(sahko()));
    connect(ui->sahko_kentta_si, SIGNAL(editingFinished()), this, SLOT(sahko()));
    connect(ui->sahko_valinta_sk, SIGNAL(currentIndexChanged(int)), this, SLOT(sahko()));
    connect(ui->sahko_valinta_si, SIGNAL(currentIndexChanged(int)), this, SLOT(sahko()));

    //connect(emptyButton, SIGNAL(clicked()), this, SLOT(onClear()));
    //connect(euroButton, SIGNAL(clicked()), this, SLOT(onEuro()));

}

void MainWindow::pituus()
{
    ui->pituus_kentta_sk->setText("pöö");
}

void MainWindow::nopeus()
{
    ui->pituus_kentta_sk->setText("pöö");
}

void MainWindow::paino()
{
    ui->pituus_kentta_sk->setText("pöö");
}

void MainWindow::lampo()
{
    ui->pituus_kentta_sk->setText("pöö");
    float i;
    double e;

}

void MainWindow::sahko()
{
    ui->pituus_kentta_sk->setText("pöö");
}

MainWindow::~MainWindow()
{
    delete ui;
}
