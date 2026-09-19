import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactElement,
  type ReactNode,
} from "react";

type TopBarActionsContextValue = {
  host: HTMLElement | null;
  registerHost: (node: HTMLElement | null) => void;
};

const TopBarActionsContext = createContext<TopBarActionsContextValue | null>(null);

/**
 * Owns the TopBar page-action slot element.
 *
 * The provider holds the element in state and `TopBar` registers it through a callback ref, so a
 * consumer that mounts anywhere below the provider obtains the real slot during the same commit
 * instead of querying the document. Registering in the commit phase means the follow-up render that
 * portals the consumer's controls still happens before the browser paints, so the controls never
 * appear in place first.
 */
export function TopBarActionsProvider({ children }: { children: ReactNode }): ReactElement {
  const [host, setHost] = useState<HTMLElement | null>(null);
  const registerHost = useCallback((node: HTMLElement | null) => setHost(node), []);
  const value = useMemo(() => ({ host, registerHost }), [host, registerHost]);

  return (
    <TopBarActionsContext.Provider value={value}>{children}</TopBarActionsContext.Provider>
  );
}

/**
 * Resolves the slot element a consumer should portal its controls into.
 *
 * Returns `null` when no `TopBar` is mounted in the current tree. Callers must keep rendering their
 * controls in place in that case, which is what makes these components usable outside the shell.
 */
export function useTopBarActionsRoot(): HTMLElement | null {
  return useContext(TopBarActionsContext)?.host ?? null;
}

/**
 * Registration callback for the component that renders the slot. `null` outside a provider, which
 * is valid: a standalone `TopBar` simply has no consumer to serve.
 */
export function useTopBarHostRegistration(): ((node: HTMLElement | null) => void) | null {
  return useContext(TopBarActionsContext)?.registerHost ?? null;
}
