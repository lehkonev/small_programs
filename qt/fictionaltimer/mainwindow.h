#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

public slots:
    void pituus_hex();
    void pituus_sk();
    void pituus_si();
    void pituus_sk_yksikko();
    void pituus_si_yksikko();

    void nopeus_hex();
    void nopeus_sk();
    void nopeus_si();
    void nopeus_sk_yksikko();
    void nopeus_si_yksikko();

    void paino_hex();
    void paino_sk();
    void paino_si();
    void paino_sk_yksikko();
    void paino_si_yksikko();

    void lampo_hex();
    void lampo_sk();
    void lampo_si();
    void lampo_sk_yksikko();
    void lampo_si_yksikko();

    void sahko_hex();
    void sahko_sk();
    void sahko_si();
    void sahko_sk_yksikko();
    void sahko_si_yksikko();

private:
    void paivita_pituus();
    void paivita_nopeus();
    void paivita_paino();
    void paivita_lampo();
    void paivita_sahko();

    Ui::MainWindow *ui;
    bool laskenta_kaynnissa_;
};

#endif // MAINWINDOW_H
