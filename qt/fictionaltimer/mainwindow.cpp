#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    laskenta_kaynnissa_ = false;
    ui->setupUi(this);
    this->setWindowTitle("Tarinan yksikkömuunnin");

    connect(ui->pituus_kentta_hex,  SIGNAL(editingFinished()),        this, SLOT(pituus_hex()));
    connect(ui->pituus_kentta_sk,   SIGNAL(editingFinished()),        this, SLOT(pituus_sk()));
    connect(ui->pituus_kentta_si,   SIGNAL(editingFinished()),        this, SLOT(pituus_si()));
    connect(ui->pituus_valinta_sk,  SIGNAL(currentIndexChanged(int)), this, SLOT(pituus_sk_yksikko()));
    connect(ui->pituus_valinta_si,  SIGNAL(currentIndexChanged(int)), this, SLOT(pituus_si_yksikko()));

    connect(ui->nopeus_kentta_hex,  SIGNAL(editingFinished()),        this, SLOT(nopeus_hex()));
    connect(ui->nopeus_kentta_sk,   SIGNAL(editingFinished()),        this, SLOT(nopeus_sk()));
    connect(ui->nopeus_kentta_si,   SIGNAL(editingFinished()),        this, SLOT(nopeus_si()));
    connect(ui->nopeus_valinta_sk,  SIGNAL(currentIndexChanged(int)), this, SLOT(nopeus_sk_yksikko()));
    connect(ui->nopeus_valinta_si,  SIGNAL(currentIndexChanged(int)), this, SLOT(nopeus_si_yksikko()));

    connect(ui->paino_kentta_hex,   SIGNAL(editingFinished()),        this, SLOT(paino_hex()));
    connect(ui->paino_kentta_sk,    SIGNAL(editingFinished()),        this, SLOT(paino_sk()));
    connect(ui->paino_kentta_si,    SIGNAL(editingFinished()),        this, SLOT(paino_si()));
    connect(ui->paino_valinta_sk,   SIGNAL(currentIndexChanged(int)), this, SLOT(paino_sk_yksikko()));
    connect(ui->paino_valinta_si,   SIGNAL(currentIndexChanged(int)), this, SLOT(paino_si_yksikko()));

    connect(ui->lampo_kentta_hex,   SIGNAL(editingFinished()),        this, SLOT(lampo_hex()));
    connect(ui->lampo_kentta_sk,    SIGNAL(editingFinished()),        this, SLOT(lampo_sk()));
    connect(ui->lampo_kentta_si,    SIGNAL(editingFinished()),        this, SLOT(lampo_si()));
    connect(ui->lampo_valinta_sk,   SIGNAL(currentIndexChanged(int)), this, SLOT(lampo_sk_yksikko()));
    connect(ui->lampo_valinta_si,   SIGNAL(currentIndexChanged(int)), this, SLOT(lampo_si_yksikko()));

    connect(ui->sahko_kentta_hex,   SIGNAL(editingFinished()),        this, SLOT(sahko_hex()));
    connect(ui->sahko_kentta_sk,    SIGNAL(editingFinished()),        this, SLOT(sahko_sk()));
    connect(ui->sahko_kentta_si,    SIGNAL(editingFinished()),        this, SLOT(sahko_si()));
    connect(ui->sahko_valinta_sk,   SIGNAL(currentIndexChanged(int)), this, SLOT(sahko_sk_yksikko()));
    connect(ui->sahko_valinta_si,   SIGNAL(currentIndexChanged(int)), this, SLOT(sahko_si_yksikko()));

    connect(ui->toiminto_lopeta,    SIGNAL(triggered(bool)),          this, SLOT(close()));

    //connect(emptyButton, SIGNAL(clicked()), this, SLOT(onClear()));
    //connect(euroButton, SIGNAL(clicked()), this, SLOT(onEuro()));

}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::pituus_hex(){}
void MainWindow::pituus_sk(){}
void MainWindow::pituus_si(){}
void MainWindow::pituus_sk_yksikko(){}
void MainWindow::pituus_si_yksikko(){}

void MainWindow::nopeus_hex(){}
void MainWindow::nopeus_sk(){}
void MainWindow::nopeus_si(){}
void MainWindow::nopeus_sk_yksikko(){}
void MainWindow::nopeus_si_yksikko(){}

void MainWindow::paino_hex(){}
void MainWindow::paino_sk(){}
void MainWindow::paino_si(){}
void MainWindow::paino_sk_yksikko(){}
void MainWindow::paino_si_yksikko(){}

void MainWindow::lampo_hex(){}
void MainWindow::lampo_sk(){}
void MainWindow::lampo_si(){}
void MainWindow::lampo_sk_yksikko(){}
void MainWindow::lampo_si_yksikko(){}

void MainWindow::sahko_hex(){}
void MainWindow::sahko_sk(){}
void MainWindow::sahko_si()
{
    ui->pituus_kentta_sk->setText("pöö");
}
void MainWindow::sahko_sk_yksikko(){}
void MainWindow::sahko_si_yksikko(){}

void MainWindow::paivita_pituus(){}
void MainWindow::paivita_nopeus(){}
void MainWindow::paivita_paino(){}
void MainWindow::paivita_lampo(){}
void MainWindow::paivita_sahko(){}
