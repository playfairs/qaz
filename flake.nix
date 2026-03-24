{
  description = "Discord bot with PostgreSQL (cross-platform)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    systems = [
      "x86_64-linux"
      "aarch64-darwin"
      "x86_64-darwin"
    ];

    forAllSystems = f:
      nixpkgs.lib.genAttrs systems (system:
        f (import nixpkgs { inherit system; })
      );
  in
  {
    devShells = forAllSystems (pkgs:
      let
        python = pkgs.python3.withPackages (ps: with ps; [
          discordpy
          python-dotenv
          psycopg2
          jishaku
          asyncpg
          colorama
        ]);
      in {
        default = pkgs.mkShell {
          buildInputs = [
            python
            pkgs.postgresql
          ];

          shellHook = ''
            export PGDATA=$PWD/.postgres
            export PGHOST=localhost
            export PGPORT=5432
            export PGUSER=$(whoami)
            export PGDATABASE=$(whoami)

            if [ ! -d "$PGDATA" ]; then
              echo "Initializing PostgreSQL..."
              initdb -D "$PGDATA"
            fi

            if ! pg_isready > /dev/null 2>&1; then
              echo "Starting PostgreSQL..."
              pg_ctl -D "$PGDATA" -l logfile start
            fi

            until pg_isready > /dev/null 2>&1; do
              sleep 0.5
            done

            createdb "$PGDATABASE" 2>/dev/null || true

            if [ ! -f "$PGDATA/.schema_applied" ]; then
              echo "Applying schema.sql..."
              psql -d "$PGDATABASE" -f bot/base/schema/schema.sql
              touch "$PGDATA/.schema_applied"
            fi

            if [ -f .env ]; then
              export $(grep -v '^#' .env | xargs)
            fi

            echo "Dev environment ready (Postgres + Python)"
          '';
        };
      }
    );

    packages = forAllSystems (pkgs:
      let
        python = pkgs.python3.withPackages (ps: with ps; [
          discordpy
          python-dotenv
          psycopg2
        ]);
      in {
        default = pkgs.writeShellScriptBin "run-bot" ''
          export PGDATA=$PWD/.postgres
          export PGHOST=localhost
          export PGPORT=5432
          export PGUSER=$(whoami)
          export PGDATABASE=$(whoami)

          if [ -f .env ]; then
            export $(grep -v '^#' .env | xargs)
          fi

          if [ -z "$TOKEN" ]; then
            echo "Error: TOKEN is not set"
            exit 1
          fi

          exec ${python}/bin/python bot/main.py
        '';
      }
    );

    apps = forAllSystems (pkgs: {
      default = {
        type = "app";
        program = "${self.packages.${pkgs.system}.default}/bin/run-bot";
      };
    });
  };
}