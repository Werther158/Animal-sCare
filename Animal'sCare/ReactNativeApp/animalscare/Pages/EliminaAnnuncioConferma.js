import React, { Component } from 'react';
import { View, Text, StyleSheet, Button, Image } from 'react-native';
import CustomHeader from '../components/Header';
import Card from '../components/Card';
import { Dimensions } from 'react-native';

const {width, height} = Dimensions.get('window');

let id_annuncio;
let title;

class EliminaAnnuncioConferma extends Component {

    eliminaAnnuncio = () => {
        fetch('http://2.224.160.133.xip.io/api/annunci/' + this.props.navigation.state.params.id_annuncio + '/dettagli/', {
            method: 'DELETE',
            headers: {
                'Authorization': 'Token ' + global.user_key
            }
        })
        .then(res => {
            this.props.navigation.navigate('ListaAnnunci');
        })
        .catch((error) => {
            this.eliminaAnnuncio;
        });

    }

    render() {
        id_annuncio = this.props.navigation.state.params.id_annuncio;
        title = "Confermi di voler eliminare l'annuncio?";
        return (
                
            <View style={styles.screen}>
                <CustomHeader parent={this.props} />
                

                <View style={{alignItems: 'center'}}>
                    <Card style={styles.inputContainer}>
                        <View style={{flexDirection: 'row'}}>
                            <Text style={styles.title}>{title}</Text>
                        </View>

                        <View style={styles.controlli}>
                            <View style={styles.buttonview}>
                                <Button title="Indietro" onPress={() => this.props.navigation.goBack(null)}/>
                            </View>
                            <View style={styles.buttonview}>
                                <Button title="Conferma" onPress={() => {this.eliminaAnnuncio();}} />
                            </View>
                        </View>
                    </Card>
                </View>
            </View>
        );
    }
}

const styles = StyleSheet.create({
    screen: {
        flex: 1
    },
    title: {
        fontSize: 20,
        marginVertical: 10
    },
    buttonview: {
        width: 110,
        paddingRight: 5,
        paddingLeft: 5
    },
    inputContainer: {
        minWidth: '96%'
    },
    controlli: {
        flexDirection: 'row',
        paddingTop: 20
    }
});

export default EliminaAnnuncioConferma;