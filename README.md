# django-stripe

Un mini projet pour apprendre les bases en Django / Stripe.

Plugins:
- [django](https://www.djangoproject.com/)
- [django-webpack-loader](https://github.com/django-webpack/django-webpack-loader)
- [stripe](https://stripe.com/docs)


## Développement Pipenv

Pour lancer le projet localement sur votre machine de développement:

```sh
$ pipenv shell
$ ./manage.py runserver
```

Vérifier que le projet se lance bien sur [http://localhost:8000/](http://localhost:8000/)


### Environnement avec pipenv

Pour installer pipenv, il vous suffit de suivre la [documentation](https://pypi.org/project/pipenv/). Ou bien simplement de lancer la commande suivantes
```sh
pip install --user pipenv
```

Il faut ensuite se mettre dans le dossier qui contient le fichier `Pipfile` (dans notre cas le dossier `app`)

Installer l'environnement :
```sh
$ pipenv install
```

Installer les packages utiles au debug :
```sh
$ pipenv install --dev
```

Lorsqu'on veut installer un nouveau paquet, ne pas utiliser `pip install` mais `pipenv install`, cela l'ajoutera automatiquement au fichier `Pipfile`.

Utiliser l'environnement :

```sh
$ pipenv shell
```

Maintenant on peut lancer toutes les commandes `migrate.py`


### Première utilisation

Lors de la première utilisation, ne pas oublier de lancer la première migration.

```sh
$ ./manage.py migrate
```

Il faudra ensuite lancer le build du thème afin de pouvoir accéder à la plateforme.
En cas de problèmes, vous pouvez vous référer à la section **Modification du thème/ReactJs**.

```sh
$ cd app/assets
$ npm run build
```

### Création d'un compte super utilisateur

Pour créer un compte super utilisateur:

```sh
$ ./manage.py createsuperuser
```

Il vous suffit ensuite de vous connecter à la [page d'administration Django](http://localhost:8000/rmas-admin/) avec les identifiants que vous avez renseigné.



## Développement Docker

Pour lancer le projet localement sur votre machine de développement:

```sh
$ docker-compose up -d --build
```

Vérifier que le projet se lance bien sur [http://localhost:8000/](http://localhost:8000/)


### Environnement avec pipenv

Pour installer docker, il vous suffit de suivre la [documentation](https://docs.docker.com/engine/install/ubuntu/).
Pour installer docker-compose, il vous suffit de suivre la [documentation](https://docs.docker.com/compose/install/).


### Première utilisation

Lors de la première utilisation, ne pas oublier de lancer la première migration.

```sh
$ docker-compose exec web ./manage.py migrate
```

Il faudra ensuite lancer le build du thème afin de pouvoir accéder à la plateforme.
En cas de problèmes, vous pouvez vous référer à la section **Modification du thème/ReactJs**.

```sh
$ docker-compose exec web /bin/bash
$ cd app/assets
$ npm run build
```


### Création d'un compte super utilisateur

Pour créer un compte super utilisateur:

```sh
$ docker-compose exec web ./manage.py createsuperuser
```

Il vous suffit ensuite de vous connecter à la [page d'administration Django](http://localhost:8000/rmas-admin/) avec les identifiants que vous avez renseigné.



## Modification du thème/ReactJs

Nous utilisons Webpack pour concaténer/minifier/bunble nos fichiers JS + SCSS.

Version NVM / NPM
```
$ nvm list
    [...]
->      v15.3.0
default -> node (-> v15.3.0)
node -> stable (-> v15.3.0) (default)
stable -> 15.3 (-> v15.3.0) (default)
[...]

$ npm --version
7.0.14
```

Pour lancer le watcher de webpack
```sh
$ cd app/assets
$ npm install
$ npm run watch
```

Pour faire un build pour la mise en prod
```sh
$ cd app/assets
$ npm run build
```


## Stripe

Pour pouvoir utiliser Stripe dans ce mini projet, il faut recupérer les clés privées/publiques du votre compte STRIPE et les renseigner dans un fichier `.env`.

```sh
echo STRIPE_PUBLISHABLE_KEY=pk_XXX >.env
echo STRIPE_SECRET_KEY=sk_XXX >>.env
echo STRIPE_SECRET_WEBHOOK=whsec_XXX >>.env
```

### Webhook

L’interface de ligne de commande Stripe est un outil destiné aux développeurs. Elle permet de créer, tester et gérer une intégration Stripe directement depuis votre terminal. Vous pouvez retrouver le documentation [ici](https://stripe.com/docs/stripe-cli#install)
Il ne vous reste plus qu'à transférer les événements à votre webhook.
```sh
./stripe listen --forward-to localhost:8000/stripe-webhook/
```

## Projet

Ce mini projet a été mis en place pour vous permettre de découvrir/apprendre/perfectionner les bases en Django / Stripe.
Le design des pages se basera sur un thème Bootstrap trouver sur [test](test).
On utilise aussi un bout de code fourni sur [stackoverflow](https://stackoverflow.com/a/41406599) pour l'avatar de la page profile.

Pour ce projet, je vais créer un webshop qui sera composé:
- D'une partie "compte utilisateur"
    - Une page de login.
    - Une page de création de compte.
    - D'une page profile pour mettre a jour les données du compte utilisateur.
- D'une partie "shop"
    - Une page listant tous les articles disponibles.
    - Une page pour voir le détail de l'article sélectionné. 
    - De plusieurs pages pour procéder au flux de paiement.
- D'un panier
    - Lié à une session pour un compte anonyme. Ce dernier est récupéré lors de la connexion au compte utilisateur.
    - Lié à un modèle User pour un utilisateur connecté 