#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QActionGroup>
#include <QLabel>
#include <QMainWindow>
#include <QTranslator>

namespace Ui {
    class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

private slots:
    void reset();
    void setLangEnglish();
    void setLangFinnish();
    void about();

private:

    Ui::MainWindow *ui_;

    QLabel *infoLabel;
};

#endif // MAINWINDOW_H
