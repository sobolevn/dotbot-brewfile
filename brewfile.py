import os
import subprocess

import dotbot


class Brew(dotbot.Plugin):
    _supported_directives = [
        'brewfile',
    ]

    _tap_command = 'brew tap homebrew/bundle'
    _install_command = 'brew bundle'
    _default_filename = 'Brewfile'

    # API methods

    def can_handle(self, directive):
        return directive in self._supported_directives

    def handle(self, directive, data):
        data = self._maybe_convert_to_dict(data)

        try:
            if not self._does_brewfile_exist(data):
                raise ValueError('Bundle file does not exist.')

            self._handle_tap()
            self._handle_install(data)
            return True
        except ValueError as e:
            self._log.error(e)
            return False

    # Utility

    @property
    def cwd(self):
        return self._context.base_directory()

    # Inner logic

    def _maybe_convert_to_dict(self, data):
        if isinstance(data, str):
            return {'file': data}
        return data
        
    def _does_brewfile_exist(self, data):
        path = os.path.join(
            self.cwd, data.get('file', self._default_filename))
        return os.path.isfile(path)

    def _build_command(self, command, data):
        def build_option(name, value):
            return '='.join(['--' + name, str(value)])

        options = [command]

        for key, value in data.items():
            options.append(build_option(key, value))

        return ' '.join(options)

    # Handlers

    def _handle_tap(self):
        with open(os.devnull, 'w') as devnull:
            result = subprocess.call(
                self._tap_command, 
                shell=True, 
                stdin=devnull, 
                stdout=devnull, 
                stderr=devnull, 
                cwd=self.cwd,
            )

            if result != 0:
                raise ValueError('Failed to tap homebrew/bundle.')

    def _handle_install(self, data):
        full_command = self._build_command(self._install_command, data)

        with open(os.devnull, 'w') as devnull:
            result = subprocess.call(
                full_command, 
                shell=True, 
                stdin=devnull, 
                stdout=devnull, 
                stderr=devnull, 
                cwd=self.cwd,
            )

            if result != 0:
                raise ValueError('Failed to install a bundle.')
        