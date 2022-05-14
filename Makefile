all: | clean render

helmaroc := "$(shell command -v python3 2>/dev/null || echo python)" helmaroc.py

clean:
	-rm -rf deploy

render/%:
	$(helmaroc) "configs/servers/$*"

render:
	$(helmaroc)


